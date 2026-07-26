import os, subprocess, tempfile
from functools import lru_cache
import numpy as np
import torch
from PIL import Image

from .config import CLIP_MODEL, CLIP_DIM, TEXT_DIM, WHISPER_MODEL

_device = "cuda" if torch.cuda.is_available() else "cpu"
_compute = "float16" if _device == "cuda" else "int8"


@lru_cache(maxsize=None)
def _get_clip():
    import clip
    return clip.load(CLIP_MODEL, device=_device)


@lru_cache(maxsize=None)
def _get_text_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


@lru_cache(maxsize=None)
def _get_whisper():
    from faster_whisper import WhisperModel
    return WhisperModel(WHISPER_MODEL, device=_device, compute_type=_compute)


def extract_clip_embed(video_path: str) -> np.ndarray:
    frames = _extract_frames(video_path)
    if not frames:
        return np.zeros(CLIP_DIM, dtype=np.float32)
    clip_model, clip_preprocess = _get_clip()
    tensors = torch.stack([clip_preprocess(f) for f in frames]).to(_device)
    with torch.no_grad():
        feats = clip_model.encode_image(tensors).float()
    mean = feats.mean(dim=0).cpu().numpy()
    norm = np.linalg.norm(mean)
    return (mean / norm).astype(np.float32) if norm > 1e-8 else mean.astype(np.float32)


def extract_text_embed(text: str) -> np.ndarray:
    if not text.strip():
        return np.zeros(TEXT_DIM, dtype=np.float32)
    return _get_text_model().encode(text, normalize_embeddings=True).astype(np.float32)


def transcribe_video(video_path: str) -> str:
    segments, _ = _get_whisper().transcribe(video_path, beam_size=1)
    return " ".join(s.text for s in segments).strip()


def _extract_frames(video_path: str) -> list[Image.Image]:
    with tempfile.TemporaryDirectory() as tmp:
        out_pattern = os.path.join(tmp, "frame_%04d.jpg")
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-vf", "fps=1", out_pattern, "-y"],
            check=True, capture_output=True,
        )
        frames = sorted(f for f in os.listdir(tmp) if f.endswith(".jpg"))
        # copy into memory before tmp dir is deleted
        return [Image.open(os.path.join(tmp, f)).convert("RGB").copy() for f in frames]
