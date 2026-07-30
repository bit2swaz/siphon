import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[3] / "scripts"))  # idhash.point_id
import numpy as np
from unittest.mock import MagicMock, patch


def _make_mock_conn(n_interactions=500):
    conn = MagicMock()
    cur = MagicMock()
    conn.cursor.return_value.__enter__ = lambda s: cur
    conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
    rows = [
        (f"u{i%50:04d}", f"v{i%100:04d}", i % 2, 0.5 + (i%2)*0.3, "watch")
        for i in range(n_interactions)
    ]
    cur.fetchall.return_value = rows
    return conn


def test_train_and_export_returns_incremented_version():
    from src.trainer import train_and_export
    mock_conn   = _make_mock_conn(500)
    mock_rdb    = MagicMock()
    mock_rdb.hget.return_value = None
    mock_qdrant = MagicMock()
    mock_minio  = MagicMock()
    mock_minio.bucket_exists.return_value = True

    with (
        patch("src.trainer.build_user_features", return_value=np.zeros(24, dtype=np.float32)),
        patch("src.trainer.build_item_features", return_value=np.zeros(256, dtype=np.float32)),
        patch("src.trainer._compute_auc", return_value=0.70),
    ):
        new_ver = train_and_export(mock_conn, mock_rdb, mock_qdrant, mock_minio, current_version=3)

    assert new_ver == 4
    assert mock_minio.put_object.called


def test_train_and_export_withholds_on_low_auc():
    from src.trainer import train_and_export
    mock_conn   = _make_mock_conn(500)
    mock_rdb    = MagicMock()
    mock_qdrant = MagicMock()
    mock_minio  = MagicMock()

    with (
        patch("src.trainer.build_user_features", return_value=np.zeros(24, dtype=np.float32)),
        patch("src.trainer.build_item_features", return_value=np.zeros(256, dtype=np.float32)),
        patch("src.trainer._compute_auc", return_value=0.55),
    ):
        new_ver = train_and_export(mock_conn, mock_rdb, mock_qdrant, mock_minio, current_version=3)

    assert new_ver == 3
    assert not mock_minio.put_object.called
