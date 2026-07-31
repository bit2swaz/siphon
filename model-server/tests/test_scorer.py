import numpy as np


def test_score_returns_correct_shape():
    from src.scorer import score_batch
    user_embed = np.random.randn(256).astype(np.float32)
    item_ids   = [f"v{i:04d}" for i in range(10)]
    item_embeds = [np.random.randn(256).astype(np.float32) for _ in range(10)]
    results = score_batch(user_embed, item_ids, item_embeds)
    assert len(results) == 10
    for vid, sc in results:
        assert isinstance(vid, str)
        assert -1.0 - 1e-5 <= sc <= 1.0 + 1e-5


def test_score_higher_for_similar_embed():
    from src.scorer import score_batch
    user_embed = np.ones(256, dtype=np.float32)
    user_embed /= np.linalg.norm(user_embed)

    similar   = user_embed.copy()
    dissimilar = -user_embed.copy()

    results = score_batch(user_embed, ["sim", "dis"], [similar, dissimilar])
    score_map = dict(results)
    assert score_map["sim"] > score_map["dis"]
