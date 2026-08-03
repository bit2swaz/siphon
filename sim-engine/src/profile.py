from __future__ import annotations
import dataclasses, os
import numpy as np

try:
    import pandas as pd
    _HAS_PANDAS = True
except ImportError:
    _HAS_PANDAS = False

from .config import DRIFT_STD


@dataclasses.dataclass
class UserProfile:
    user_id:         str
    interest_vec:    np.ndarray   # shape=(256,), L2-normalised
    watch_frac_bias: float
    like_rate_bias:  float


def watch_probability(profile: UserProfile, video_embed: list[float]) -> float:
    """P(watch) = sigmoid(interest · video_embed + bias)."""
    v = np.array(video_embed, dtype=np.float32)
    norm = np.linalg.norm(v)
    if norm > 1e-8:
        v /= norm
    dot = float(np.dot(profile.interest_vec, v))
    x = dot + profile.watch_frac_bias
    return float(1.0 / (1.0 + np.exp(-x * 5.0)))  # scale factor sharpens sigmoid


def drift(profile: UserProfile) -> UserProfile:
    """Gaussian random walk on interest vector, re-normalised."""
    noise = np.random.randn(256).astype(np.float32) * DRIFT_STD
    new_vec = profile.interest_vec + noise
    norm = np.linalg.norm(new_vec)
    new_vec = new_vec / norm if norm > 1e-8 else new_vec
    return dataclasses.replace(profile, interest_vec=new_vec)


def load_profiles(n: int, kuairec_path: str = "data/small_matrix.csv") -> list[UserProfile]:
    """Load n user profiles. Uses KuaiRec watch_ratio for bias if available, else random."""
    biases = None
    if _HAS_PANDAS and os.path.exists(kuairec_path):
        stats = pd.read_csv(kuairec_path).groupby("user_id")["watch_ratio"].mean().to_numpy()
        biases = stats - 0.5  # centre around 0

    rng = np.random.default_rng(42)
    profiles = []
    for i in range(n):
        vec = rng.standard_normal(256).astype(np.float32)
        vec /= np.linalg.norm(vec)
        if biases is not None:
            bias = float(biases[i % len(biases)])
            like = max(0.0, bias * 0.3)
        else:
            bias = float(rng.normal(0.0, 0.1))
            like = float(rng.uniform(0.05, 0.2))
        profiles.append(UserProfile(f"u{i:06d}", vec, bias, like))
    return profiles
