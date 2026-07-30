import torch
import torch.nn as nn
import torch.nn.functional as F


def _mlp(dims: list[int]) -> nn.Sequential:
    layers = []
    for i in range(len(dims) - 1):
        layers.append(nn.Linear(dims[i], dims[i + 1]))
        if i < len(dims) - 2:
            layers.append(nn.ReLU())
    return nn.Sequential(*layers)


class TwoTower(nn.Module):
    def __init__(self, user_feat_dim: int, item_feat_dim: int, embed_dim: int):
        super().__init__()
        self._user_tower = _mlp([user_feat_dim, 512, embed_dim])
        self._item_tower = _mlp([item_feat_dim, embed_dim])

    def user_embed(self, user_feat: torch.Tensor) -> torch.Tensor:
        return F.normalize(self._user_tower(user_feat), dim=-1)

    def item_embed(self, item_feat: torch.Tensor) -> torch.Tensor:
        return F.normalize(self._item_tower(item_feat), dim=-1)

    def forward(self, user_feat: torch.Tensor, item_feat: torch.Tensor) -> torch.Tensor:
        u = self.user_embed(user_feat)
        v = self.item_embed(item_feat)
        return (u * v).sum(dim=-1)
