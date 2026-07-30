import numpy as np
from unittest.mock import MagicMock

CATEGORIES = ["music","comedy","sports","food","travel","tech","fashion","gaming","news","dance",
              "fitness","pets","art","science","nature","diy","beauty","cars","finance","education"]


def test_build_user_features_shape():
    from src.features import build_user_features
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__ = lambda s: mock_cur
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    mock_cur.fetchall.return_value = [
        (0.8, "watch", "u000001_v000001"),
        (0.3, "skip",  "u000001_v000002"),
        (1.0, "like",  "u000001_v000003"),
        (0.6, "watch", "u000001_v000004"),
        (0.9, "replay","u000001_v000005"),
        (0.2, "skip",  "u000001_v000006"),
        (0.7, "watch", "u000001_v000007"),
        (1.0, "share", "u000001_v000008"),
        (0.4, "watch", "u000001_v000009"),
        (0.5, "watch", "u000001_v000010"),
    ]
    feat = build_user_features("u000001", mock_conn)
    assert feat.shape == (24,), f"expected (24,), got {feat.shape}"
    assert feat.dtype == np.float32
    assert (feat[:4] >= 0).all() and (feat[:4] <= 1).all()
    assert abs(feat[4:].sum() - 1.0) < 1e-5 or feat[4:].sum() == 0.0


def test_build_user_features_no_history():
    from src.features import build_user_features
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__ = lambda s: mock_cur
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    mock_cur.fetchall.return_value = []
    feat = build_user_features("u_new", mock_conn)
    assert feat.shape == (24,)
    assert (feat == 0).all()
