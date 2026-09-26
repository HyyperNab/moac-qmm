"""Outcome tracker — SPOF #28 annihilated.

Persistent feedback loop that tracks predictions vs. actual outcomes
and feeds back into all models. The engine is no longer one-shot — it
learns from every execution.

Production hardening:
- D-13: ``get_accuracy_metrics`` contained dead correction-matching
  code; metrics are now computed from the corrections themselves.
- Persistence is explicit: pass ``log_path`` (or call ``save``/``load``)
  to persist JSONL; the engine never writes to the filesystem silently.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class OutcomeTracker:
    """Tracks predicted vs. actual outcomes for continuous model improvement."""

    def __init__(self, log_path: str | Path | None = None) -> None:
        self.log_path = Path(log_path) if log_path else None
        self.predictions: list[dict[str, Any]] = []
        self.outcomes: list[dict[str, Any]] = []
        self.corrections: list[dict[str, Any]] = []

    def log_prediction(self, prediction_id: str, prediction: dict[str, Any]) -> None:
        """Log a prediction made by the engine."""
        entry = {
            "id": prediction_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prediction": prediction,
            "outcome": None,
        }
        self.predictions.append(entry)
        if self.log_path is not None:
            self._append_jsonl(self.log_path, entry)

    def log_outcome(self, prediction_id: str, actual_outcome: dict[str, Any]) -> None:
        """Log the actual outcome for a previous prediction."""
        for entry in self.predictions:
            if entry["id"] == prediction_id:
                entry["outcome"] = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data": actual_outcome,
                }
                correction = self._compute_correction(entry["prediction"], actual_outcome)
                if correction is not None:
                    self.corrections.append({"id": prediction_id, "fields": correction})
                break

    @staticmethod
    def _compute_correction(
        prediction: dict[str, Any], actual: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Numeric difference between prediction and actual outcome."""
        corrections: dict[str, Any] = {}
        keys = set(list(prediction.keys()) + list(actual.keys()))
        for key in keys:
            pred_val = prediction.get(key)
            actual_val = actual.get(key)
            if (
                pred_val is not None
                and actual_val is not None
                and isinstance(pred_val, int | float)
                and isinstance(actual_val, int | float)
            ):
                corrections[key] = {
                    "predicted": pred_val,
                    "actual": actual_val,
                    "error": abs(pred_val - actual_val),
                    "relative_error": abs(pred_val - actual_val) / (abs(actual_val) + 1e-8),
                }
        return corrections if corrections else None

    def get_accuracy_metrics(self) -> dict[str, Any]:
        """Accuracy metrics across all resolved predictions."""
        resolved = [e for e in self.predictions if e["outcome"] is not None]
        if not resolved:
            return {"n_resolved": 0, "mean_relative_error": None}

        relative_errors = [
            fields["relative_error"]
            for corr in self.corrections
            for fields in corr["fields"].values()
        ]
        return {
            "n_predictions": len(self.predictions),
            "n_resolved": len(resolved),
            "n_corrections": len(self.corrections),
            "mean_relative_error": (
                sum(relative_errors) / len(relative_errors) if relative_errors else None
            ),
        }

    @staticmethod
    def _append_jsonl(path: Path, entry: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, default=str) + "\n")

    def save(self, path: str | Path | None = None) -> None:
        """Save tracker state to JSON."""
        save_path = Path(path) if path else self.log_path
        if save_path is None:
            return
        data = {
            "predictions": self.predictions,
            "n_total": len(self.predictions),
            "n_resolved": sum(1 for p in self.predictions if p["outcome"]),
        }
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def load(self, path: str | Path | None = None) -> None:
        """Load tracker state from JSON."""
        load_path = Path(path) if path else self.log_path
        if load_path is None or not load_path.exists():
            return
        data = json.loads(load_path.read_text(encoding="utf-8"))
        self.predictions = list(data.get("predictions", []))


__all__ = ["OutcomeTracker"]
