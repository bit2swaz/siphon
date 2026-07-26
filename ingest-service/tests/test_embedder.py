import numpy as np
import tempfile, os

def test_clip_embed_shape():
    from src.embedder import extract_clip_embed
    import subprocess
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        tmp = f.name
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=1",
        "-c:v", "libx264", "-t", "1", tmp
    ], check=True, capture_output=True)
    embed = extract_clip_embed(tmp)
    os.unlink(tmp)
    assert embed.shape == (512,)
    assert embed.dtype == np.float32
    assert abs(np.linalg.norm(embed) - 1.0) < 1e-5

def test_text_embed_shape():
    from src.embedder import extract_text_embed
    embed = extract_text_embed("a funny cat video")
    assert embed.shape == (384,)
    assert embed.dtype == np.float32
    assert abs(np.linalg.norm(embed) - 1.0) < 1e-5
