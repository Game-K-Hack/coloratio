"""Conversions de couleurs et quantification de palette."""

from collections import Counter

import numpy as np
from PIL import Image
from PyQt5.QtGui import QImage, QPixmap


def pil_to_qpixmap(pil_img: Image.Image) -> QPixmap:
    if pil_img.mode != "RGBA":
        pil_img = pil_img.convert("RGBA")
    data = pil_img.tobytes("raw", "RGBA")
    qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg.copy())


def quantize_colors(pil_img: Image.Image, max_colors: int = 32):
    """Retourne [((r,g,b), count), ...] tries par frequence decroissante."""
    small = pil_img.convert("RGB")
    if max(small.size) > 400:
        small.thumbnail((400, 400))
    q = small.quantize(colors=max_colors, method=Image.Quantize.FASTOCTREE)
    palette = q.getpalette()[: max_colors * 3]
    counts = Counter(q.getdata())
    return [
        ((palette[i * 3], palette[i * 3 + 1], palette[i * 3 + 2]), c)
        for i, c in counts.most_common()
    ]


def rgb_to_hsv_np(rgb: np.ndarray) -> np.ndarray:
    arr = rgb.astype(np.float32) / 255.0
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    mx = np.max(arr, axis=-1)
    mn = np.min(arr, axis=-1)
    diff = mx - mn
    safe = np.where(diff == 0, 1, diff)

    rc = np.where((diff != 0) & (mx == r), ((g - b) / safe) % 6, 0)
    gc = np.where((diff != 0) & (mx == g), ((b - r) / safe) + 2, 0)
    bc = np.where((diff != 0) & (mx == b), ((r - g) / safe) + 4, 0)
    h = ((rc + gc + bc) / 6.0) % 1.0

    s = np.where(mx == 0, 0, diff / np.where(mx == 0, 1, mx))
    v = mx
    return np.stack([h, s, v], axis=-1)


def hsv_to_rgb_np(hsv: np.ndarray) -> np.ndarray:
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    h = (h % 1.0) * 6.0
    i = np.floor(h).astype(np.int32)
    f = h - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    i_mod = i % 6
    r = np.choose(i_mod, [v, q, p, p, t, v])
    g = np.choose(i_mod, [t, v, v, q, p, p])
    b = np.choose(i_mod, [p, p, t, v, v, q])
    return np.clip(np.stack([r, g, b], axis=-1) * 255.0, 0, 255).astype(np.uint8)
