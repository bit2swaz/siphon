import torch


def test_two_tower_output_shape():
    from src.model import TwoTower
    from src.config import USER_FEAT_DIM, ITEM_FEAT_DIM, EMBED_DIM
    model = TwoTower(USER_FEAT_DIM, ITEM_FEAT_DIM, EMBED_DIM)
    user_feat = torch.randn(8, USER_FEAT_DIM)
    item_feat = torch.randn(8, ITEM_FEAT_DIM)
    scores = model(user_feat, item_feat)
    assert scores.shape == (8,), f"expected (8,), got {scores.shape}"


def test_two_tower_scores_in_range():
    from src.model import TwoTower
    from src.config import USER_FEAT_DIM, ITEM_FEAT_DIM, EMBED_DIM
    model = TwoTower(USER_FEAT_DIM, ITEM_FEAT_DIM, EMBED_DIM)
    user_feat = torch.randn(4, USER_FEAT_DIM)
    item_feat = torch.randn(4, ITEM_FEAT_DIM)
    scores = model(user_feat, item_feat)
    assert scores.min() >= -1.0 - 1e-5
    assert scores.max() <=  1.0 + 1e-5


def test_user_embed_l2_normalised():
    from src.model import TwoTower
    from src.config import USER_FEAT_DIM, ITEM_FEAT_DIM, EMBED_DIM
    model = TwoTower(USER_FEAT_DIM, ITEM_FEAT_DIM, EMBED_DIM)
    user_feat = torch.randn(4, USER_FEAT_DIM)
    u = model.user_embed(user_feat)
    norms = u.norm(dim=-1)
    assert torch.allclose(norms, torch.ones(4), atol=1e-5)
