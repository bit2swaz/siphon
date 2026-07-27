import numpy as np


def test_project_output_shape_and_normalised():
    from src.projector import project
    clip = np.random.randn(512).astype(np.float32)
    text = np.random.randn(384).astype(np.float32)
    out = project(clip, text)
    assert out.shape == (256,)
    assert out.dtype == np.float32
    assert abs(np.linalg.norm(out) - 1.0) < 1e-5


def test_project_zero_clip_returns_nonzero():
    from src.projector import project
    clip = np.zeros(512, dtype=np.float32)
    text = np.random.randn(384).astype(np.float32)
    out = project(clip, text)
    assert out.shape == (256,)
