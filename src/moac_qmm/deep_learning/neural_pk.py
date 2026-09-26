"""Neural PK predictor — SPOF #24 annihilated.

A lightweight numpy-based neural network that predicts pharmacokinetic
parameters (clearance rate, half-life, volume of distribution) from
patient features. Replaces hardcoded PK constants with learned,
patient-specific predictions.

Architecture: 3-layer MLP with ReLU activation.
Training: gradient descent via backpropagation (numpy only).
Uncertainty: MC Dropout approximation at inference time.

Production hardening (SPOF #38): model persistence switched from
``pickle`` (arbitrary code execution on load) to JSON.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, ClassVar

import numpy as np

logger = logging.getLogger(__name__)


class NeuralPKPredictor:
    """Neural network for pharmacokinetic parameter prediction.

    Input features (normalized): age, biological_age, gfr, albumin,
    hepatic_flow, cyp2c19_activity, cyp3a4_activity, spo2, body_weight,
    sex.

    Outputs: clearance_rate, t_half, vd — each with an epistemic
    uncertainty estimate (MC Dropout) and a confidence score.
    """

    FEATURE_NAMES: ClassVar[list[str]] = [
        "age",
        "bio_age",
        "gfr",
        "albumin",
        "hepatic_flow",
        "cyp2c19_activity",
        "cyp3a4_activity",
        "spo2",
        "body_weight",
        "sex",
    ]

    OUTPUT_NAMES: ClassVar[list[str]] = ["clearance_rate", "t_half", "vd"]

    def __init__(
        self,
        hidden_size: int = 32,
        learning_rate: float = 0.001,
        seed: int = 42,
    ) -> None:
        self.hidden_size = hidden_size
        self.lr = learning_rate
        self.rng = np.random.default_rng(seed)
        self.is_trained = False
        self.training_history: list[float] = []

        input_size = len(self.FEATURE_NAMES)
        output_size = len(self.OUTPUT_NAMES)

        # Xavier initialization
        self.W1 = self.rng.standard_normal((input_size, hidden_size)) * np.sqrt(2.0 / input_size)
        self.b1 = np.zeros(hidden_size)
        self.W2 = self.rng.standard_normal((hidden_size, hidden_size)) * np.sqrt(2.0 / hidden_size)
        self.b2 = np.zeros(hidden_size)
        self.W3 = self.rng.standard_normal((hidden_size, output_size)) * np.sqrt(2.0 / hidden_size)
        self.b3 = np.zeros(output_size)

        self.feature_mean = np.zeros(input_size)
        self.feature_std = np.ones(input_size)
        self.output_mean = np.zeros(output_size)
        self.output_std = np.ones(output_size)

    @staticmethod
    def _relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    @staticmethod
    def _relu_deriv(x: np.ndarray) -> np.ndarray:
        return (x > 0).astype(float)

    def _forward(self, x: np.ndarray) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """Forward pass. Returns output and cache for backprop."""
        z1 = x @ self.W1 + self.b1
        a1 = self._relu(z1)
        z2 = a1 @ self.W2 + self.b2
        a2 = self._relu(z2)
        z3 = a2 @ self.W3 + self.b3
        cache: dict[str, np.ndarray] = {"x": x, "z1": z1, "a1": a1, "z2": z2, "a2": a2, "z3": z3}
        return z3, cache

    def _backward(
        self, cache: dict[str, np.ndarray], y_true: np.ndarray, y_pred: np.ndarray
    ) -> dict[str, np.ndarray]:
        """Backpropagation. Returns gradients."""
        m = y_true.shape[0]
        dz3 = (y_pred - y_true) / m
        dW3 = cache["a2"].T @ dz3
        db3 = np.sum(dz3, axis=0)

        da2 = dz3 @ self.W3.T
        dz2 = da2 * self._relu_deriv(cache["z2"])
        dW2 = cache["a1"].T @ dz2
        db2 = np.sum(dz2, axis=0)

        da1 = dz2 @ self.W2.T
        dz1 = da1 * self._relu_deriv(cache["z1"])
        dW1 = cache["x"].T @ dz1
        db1 = np.sum(dz1, axis=0)

        grads: dict[str, np.ndarray] = {
            "W1": dW1,
            "b1": db1,
            "W2": dW2,
            "b2": db2,
            "W3": dW3,
            "b3": db3,
        }
        return grads

    def _normalize_features(self, features: np.ndarray) -> np.ndarray:
        return (features - self.feature_mean) / (self.feature_std + 1e-8)

    def _denormalize_output(self, output: np.ndarray) -> np.ndarray:
        return output * self.output_std + self.output_mean

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 500,
        batch_size: int = 32,
        verbose: bool = False,
    ) -> list[float]:
        """Train the network with mini-batch gradient descent.

        Args:
            X: Training features, shape (n_samples, n_features).
            y: Training targets, shape (n_samples, n_outputs).
            epochs: Number of training epochs.
            batch_size: Mini-batch size.
            verbose: Log the loss every 100 epochs.

        Returns:
            Loss history per epoch.
        """
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)

        if X.ndim != 2 or X.shape[1] != len(self.FEATURE_NAMES):
            msg = f"Expected (*, {len(self.FEATURE_NAMES)}) features, got {X.shape}"
            raise ValueError(msg)
        if y.ndim != 2 or y.shape[1] != len(self.OUTPUT_NAMES):
            msg = f"Expected (*, {len(self.OUTPUT_NAMES)}) outputs, got {y.shape}"
            raise ValueError(msg)

        # Compute normalization parameters
        self.feature_mean = X.mean(axis=0)
        self.feature_std = X.std(axis=0) + 1e-8
        self.output_mean = y.mean(axis=0)
        self.output_std = y.std(axis=0) + 1e-8

        X_norm = self._normalize_features(X)
        y_norm = (y - self.output_mean) / self.output_std

        n_samples = X_norm.shape[0]
        self.training_history = []

        for epoch in range(epochs):
            perm = self.rng.permutation(n_samples)
            X_shuffled = X_norm[perm]
            y_shuffled = y_norm[perm]

            epoch_loss = 0.0
            n_batches = 0

            for i in range(0, n_samples, batch_size):
                xb = X_shuffled[i : i + batch_size]
                yb = y_shuffled[i : i + batch_size]

                pred, cache = self._forward(xb)
                loss = np.mean((pred - yb) ** 2)
                epoch_loss += loss
                n_batches += 1

                grads = self._backward(cache, yb, pred)

                self.W1 -= self.lr * grads["W1"]
                self.b1 -= self.lr * grads["b1"]
                self.W2 -= self.lr * grads["W2"]
                self.b2 -= self.lr * grads["b2"]
                self.W3 -= self.lr * grads["W3"]
                self.b3 -= self.lr * grads["b3"]

            avg_loss = epoch_loss / max(1, n_batches)
            self.training_history.append(avg_loss)

            if verbose and (epoch + 1) % 100 == 0:
                logger.info("Epoch %d/%d, Loss: %.6f", epoch + 1, epochs, avg_loss)

        self.is_trained = True
        logger.info("Training complete. Final loss: %.6f", self.training_history[-1])
        return self.training_history

    def predict(self, features: dict[str, Any], n_mc_samples: int = 50) -> dict[str, Any]:
        """Predict PK parameters with MC-Dropout uncertainty.

        Falls back to biophysical heuristics when untrained.
        """
        if not self.is_trained:
            logger.info("Model not trained. Using heuristic defaults.")
            return self._heuristic_predict(features)

        x = np.array(
            [
                features.get("age", 45),
                features.get("bio_age", features.get("age", 45)),
                features.get("gfr", 90),
                features.get("albumin", 4.0),
                features.get("hepatic_flow", 1500),
                features.get("cyp2c19_activity", 1.0),
                features.get("cyp3a4_activity", 1.0),
                features.get("spo2", 98),
                features.get("body_weight", 70),
                features.get("sex", 0),
            ]
        ).reshape(1, -1)

        x_norm = self._normalize_features(x)

        predictions = []
        dropout_rate = 0.1

        for _ in range(n_mc_samples):
            pred, _ = self._forward_with_dropout(x_norm, dropout_rate)
            pred_denorm = self._denormalize_output(pred)
            predictions.append(pred_denorm.flatten())

        predictions_arr = np.array(predictions)

        mean_pred = predictions_arr.mean(axis=0)
        uncertainty = predictions_arr.std(axis=0)

        confidence = 1.0 / (1.0 + uncertainty / (np.abs(mean_pred) + 1e-8))

        result: dict[str, Any] = {}
        for i, name in enumerate(self.OUTPUT_NAMES):
            result[name] = float(mean_pred[i])
            result[f"{name}_uncertainty"] = float(uncertainty[i])
        result["confidence"] = float(np.mean(confidence))
        result["n_mc_samples"] = n_mc_samples

        return result

    def _forward_with_dropout(
        self, x: np.ndarray, rate: float
    ) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """Forward pass with MC Dropout for uncertainty estimation."""
        z1 = x @ self.W1 + self.b1
        a1 = self._relu(z1)
        mask1 = self.rng.binomial(1, 1 - rate, a1.shape) / (1 - rate)
        a1 *= mask1

        z2 = a1 @ self.W2 + self.b2
        a2 = self._relu(z2)
        mask2 = self.rng.binomial(1, 1 - rate, a2.shape) / (1 - rate)
        a2 *= mask2

        z3 = a2 @ self.W3 + self.b3
        return z3, {}

    def _heuristic_predict(self, features: dict[str, Any]) -> dict[str, Any]:
        """Fallback when the model is not trained — biophysical heuristics."""
        gfr = features.get("gfr", 90)
        albumin = features.get("albumin", 4.0)
        cyp_activity = features.get("cyp2c19_activity", 1.0)

        clearance = (gfr / 90.0) * 0.3 + cyp_activity * 0.5
        vd = 0.25 * (1 + (4.0 - albumin) * 0.3)
        t_half = (0.693 * vd) / max(0.01, clearance)

        return {
            "clearance_rate": clearance,
            "t_half": t_half,
            "vd": vd,
            "clearance_rate_uncertainty": 0.3,
            "t_half_uncertainty": 0.4,
            "vd_uncertainty": 0.2,
            "confidence": 0.5,
            "n_mc_samples": 0,
            "heuristic": True,
        }

    def save(self, path: str | Path) -> None:
        """Save model weights to JSON (SPOF #38: no pickle, no code execution)."""
        state = {
            "W1": self.W1.tolist(),
            "b1": self.b1.tolist(),
            "W2": self.W2.tolist(),
            "b2": self.b2.tolist(),
            "W3": self.W3.tolist(),
            "b3": self.b3.tolist(),
            "feature_mean": self.feature_mean.tolist(),
            "feature_std": self.feature_std.tolist(),
            "output_mean": self.output_mean.tolist(),
            "output_std": self.output_std.tolist(),
            "is_trained": self.is_trained,
            "training_history": self.training_history,
        }
        Path(path).write_text(json.dumps(state), encoding="utf-8")

    def load(self, path: str | Path) -> None:
        """Load model weights from JSON."""
        state = json.loads(Path(path).read_text(encoding="utf-8"))
        self.W1 = np.asarray(state["W1"], dtype=float)
        self.b1 = np.asarray(state["b1"], dtype=float)
        self.W2 = np.asarray(state["W2"], dtype=float)
        self.b2 = np.asarray(state["b2"], dtype=float)
        self.W3 = np.asarray(state["W3"], dtype=float)
        self.b3 = np.asarray(state["b3"], dtype=float)
        self.feature_mean = np.asarray(state["feature_mean"], dtype=float)
        self.feature_std = np.asarray(state["feature_std"], dtype=float)
        self.output_mean = np.asarray(state["output_mean"], dtype=float)
        self.output_std = np.asarray(state["output_std"], dtype=float)
        self.is_trained = bool(state["is_trained"])
        self.training_history = [float(v) for v in state["training_history"]]


__all__ = ["NeuralPKPredictor"]
