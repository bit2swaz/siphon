import numpy as np


def test_watch_probability_similar_interest_high():
    from src.profile import UserProfile, watch_probability
    vec = np.ones(256, dtype=np.float32)
    vec /= np.linalg.norm(vec)
    profile = UserProfile("u1", interest_vec=vec, watch_frac_bias=0.0, like_rate_bias=0.0)
    # video embed aligned with interest -> high P(watch)
    p = watch_probability(profile, vec.tolist())
    assert p > 0.5, f"expected > 0.5, got {p}"


def test_watch_probability_opposite_interest_low():
    from src.profile import UserProfile, watch_probability
    vec = np.ones(256, dtype=np.float32)
    vec /= np.linalg.norm(vec)
    profile = UserProfile("u1", interest_vec=vec, watch_frac_bias=0.0, like_rate_bias=0.0)
    anti = -vec
    p = watch_probability(profile, anti.tolist())
    assert p < 0.5, f"expected < 0.5, got {p}"


def test_drift_changes_interest():
    from src.profile import UserProfile, drift
    vec = np.ones(256, dtype=np.float32)
    vec /= np.linalg.norm(vec)
    profile = UserProfile("u1", interest_vec=vec.copy(), watch_frac_bias=0.0, like_rate_bias=0.0)
    new_profile = drift(profile)
    assert not np.allclose(profile.interest_vec, new_profile.interest_vec)
    # still normalised
    assert abs(np.linalg.norm(new_profile.interest_vec) - 1.0) < 1e-5


def test_load_profiles_returns_n():
    from src.profile import load_profiles
    profiles = load_profiles(10, kuairec_path="nonexistent.csv")
    assert len(profiles) == 10
    for p in profiles:
        assert p.interest_vec.shape == (256,)
        assert abs(np.linalg.norm(p.interest_vec) - 1.0) < 1e-5
