"""Reinforcement learning treatment optimizer — SPOF #27 annihilated.

Q-learning agent that discovers optimal treatment policies through
simulated episodes. Replaces static treatment recommendations with
learned policies that improve with experience.

State: (pathogen_strategy, immune_status, biofilm, subtherapeutic)
Actions: the 5 treatment strategies.
Reward: treatment efficacy - pathogen survival (payoff matrix).

Production defect fixes:
- D-11: epsilon decay was a no-op (``epsilon_decay_unused()`` returned
  1.0 "to avoid linting issues") — exploration never decayed. Now the
  configured ``epsilon_decay`` is applied.
- D-12: global ``np.random`` replaced by an injectable, seedable
  ``numpy.random.Generator`` (deterministic, thread-safe).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class ReinforcementLearningOptimizer:
    """Q-learning agent for treatment optimization."""

    n_states: int = 40  # 5 pathogen × 2 immune × 2 biofilm × 2 subtherapeutic
    n_actions: int = 5  # 5 treatment strategies
    alpha: float = 0.1  # learning rate
    gamma: float = 0.95  # discount factor
    epsilon: float = 1.0  # exploration rate (decays)
    epsilon_min: float = 0.05
    epsilon_decay: float = 0.995

    Q: np.ndarray = field(init=False)
    episode_rewards: list[float] = field(default_factory=list)
    n_episodes: int = 0

    def __post_init__(self) -> None:
        self.Q = np.zeros((self.n_states, self.n_actions))
        self.rng = np.random.default_rng()

    def with_seed(self, seed: int) -> ReinforcementLearningOptimizer:
        """Return self with a re-seeded RNG (deterministic training)."""
        self.rng = np.random.default_rng(seed)
        return self

    def _encode_state(
        self,
        pathogen_strategy_idx: int,
        immune_high: bool,
        biofilm: bool,
        subtherapeutic: bool,
    ) -> int:
        """Encode the clinical state into a single Q-table index."""
        return (
            pathogen_strategy_idx * 8
            + int(immune_high) * 4
            + int(biofilm) * 2
            + int(subtherapeutic)
        )

    def choose_action(self, state: int, greedy: bool = False) -> int:
        """Epsilon-greedy action selection."""
        if not greedy and self.rng.random() < self.epsilon:
            return int(self.rng.integers(self.n_actions))
        return int(np.argmax(self.Q[state]))

    def update(self, state: int, action: int, reward: float, next_state: int) -> None:
        """Q-learning update rule."""
        best_next = np.max(self.Q[next_state])
        td_target = reward + self.gamma * best_next
        td_error = td_target - self.Q[state, action]
        self.Q[state, action] += self.alpha * td_error

        # Decay exploration (D-11 fix)
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.n_episodes += 1
        self.episode_rewards.append(reward)

    def train_episode(self, payoff_matrix: np.ndarray, max_steps: int = 20) -> float:
        """Simulate one treatment episode against a payoff matrix."""
        state = int(self.rng.integers(self.n_states))
        total_reward = 0.0

        for _ in range(max_steps):
            action = self.choose_action(state)

            p_idx = state // 8
            t_idx = action

            if p_idx < payoff_matrix.shape[0] and t_idx < payoff_matrix.shape[1]:
                t_payoff = payoff_matrix[p_idx, t_idx, 1]
                p_payoff = payoff_matrix[p_idx, t_idx, 0]
                reward = float(t_payoff - p_payoff * 0.5)
            else:
                reward = 0.0

            next_state = int(self.rng.integers(self.n_states))
            self.update(state, action, reward, next_state)
            total_reward += reward
            state = next_state

        return total_reward

    def train(
        self,
        payoff_matrix: np.ndarray,
        episodes: int = 200,
        max_steps: int = 20,
    ) -> list[float]:
        """Train for a batch of episodes; returns per-episode rewards."""
        return [self.train_episode(payoff_matrix, max_steps) for _ in range(episodes)]

    def get_optimal_policy(self) -> dict[int, int]:
        """Greedy policy: state → best action."""
        return {s: int(np.argmax(self.Q[s])) for s in range(self.n_states)}

    def recommend_treatment(
        self,
        pathogen_strategy_idx: int,
        immune_high: bool,
        biofilm: bool,
        subtherapeutic: bool,
    ) -> int:
        """Recommend the best treatment action for a clinical state."""
        state = self._encode_state(pathogen_strategy_idx, immune_high, biofilm, subtherapeutic)
        return self.choose_action(state, greedy=True)

    def summary(self) -> dict[str, Any]:
        """Training summary statistics."""
        recent = self.episode_rewards[-100:] if self.episode_rewards else []
        return {
            "episodes_trained": self.n_episodes,
            "epsilon": self.epsilon,
            "avg_reward_last_100": float(np.mean(recent)) if recent else 0.0,
            "q_table_max": float(self.Q.max()),
            "q_table_nonzero": int(np.count_nonzero(self.Q)),
        }


__all__ = ["ReinforcementLearningOptimizer"]
