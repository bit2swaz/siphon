"""
Run AFTER sim-engine has been running long enough for the first training run
(RETRAIN_EVERY_N=10000 interactions; with SIM_SPEED_MULTIPLIER=10 this takes
roughly 2-3 minutes of wall-clock time). Run manually or in a long-running CI job.
"""
import time
import psycopg2
import pytest

PG = dict(host="localhost", port=5432, dbname="siphon", user="siphon", password="siphon")

def test_first_training_run_auc_passes_gate():
    """Wait up to 5 minutes for the first completed training run, assert AUC >= 0.65."""
    conn = psycopg2.connect(**PG)
    deadline = time.time() + 300  # 5 min
    try:
        while time.time() < deadline:
            cur = conn.cursor()
            cur.execute(
                "SELECT version, auc FROM training_runs WHERE finished_at IS NOT NULL ORDER BY version DESC LIMIT 1"
            )
            row = cur.fetchone()
            if row:
                version, auc = row
                assert auc is not None, f"Training run v{version} has no AUC recorded"
                assert auc >= 0.65, f"Training run v{version} AUC {auc:.4f} below gate 0.65"
                print(f"PASS: training run v{version} AUC={auc:.4f}")
                return
            time.sleep(10)
        pytest.fail("No completed training run within 5 minutes. Check training-service logs.")
    finally:
        conn.close()
