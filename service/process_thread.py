import colorsys
import numpy as np
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal

from service.color_utils import rgb_to_hsv_np, hsv_to_rgb_np


class ProcessThread(QThread):
    """
    Modes de masquage :
      - "index"     : utilise index_map (un pixel = un cluster), 100% des pixels
                      du cluster sont touches. Pas de tolerance.
      - "tolerance" : compare chaque pixel aux RGB selectionnes a +/- tol.
    """

    finished_img = pyqtSignal(object)

    def __init__(self, base_img, selected_rgbs, target_rgb,
                 mode="index", tolerance=12,
                 index_map=None, selected_indices=None):
        super().__init__()
        self.base_img = base_img
        self.selected_rgbs = selected_rgbs
        self.target_rgb = target_rgb
        self.mode = mode
        self.tolerance = tolerance
        self.index_map = index_map
        self.selected_indices = selected_indices or []

    def run(self):
        if not self.selected_rgbs:
            self.finished_img.emit(self.base_img.copy())
            return

        img = self.base_img.convert("RGBA")
        arr = np.array(img)
        rgb = arr[..., :3]
        alpha = arr[..., 3:4]

        ref_rgb = np.array(self.selected_rgbs, dtype=np.float32).mean(axis=0)
        ref_hsv = colorsys.rgb_to_hsv(*(ref_rgb / 255.0))
        target_hsv = colorsys.rgb_to_hsv(*(np.array(self.target_rgb) / 255.0))
        dh = target_hsv[0] - ref_hsv[0]
        ds = target_hsv[1] - ref_hsv[1]
        dv = target_hsv[2] - ref_hsv[2]

        mask = self._build_mask(rgb)
        if not mask.any():
            self.finished_img.emit(self.base_img.copy())
            return

        sub_hsv = rgb_to_hsv_np(rgb[mask])
        sub_hsv[..., 0] = (sub_hsv[..., 0] + dh) % 1.0
        sub_hsv[..., 1] = np.clip(sub_hsv[..., 1] + ds, 0.0, 1.0)
        sub_hsv[..., 2] = np.clip(sub_hsv[..., 2] + dv, 0.0, 1.0)

        out = rgb.copy()
        out[mask] = hsv_to_rgb_np(sub_hsv)
        result = np.concatenate([out, alpha], axis=-1)
        self.finished_img.emit(Image.fromarray(result, mode="RGBA"))

    def _build_mask(self, rgb):
        if self.mode == "index" and self.index_map is not None and self.selected_indices:
            sel = np.array(self.selected_indices, dtype=np.int32)
            return np.isin(self.index_map, sel)

        # Mode tolerance (rapide, comparaison par canal)
        tol = max(0, int(self.tolerance))
        mask = np.zeros(rgb.shape[:2], dtype=bool)
        for c in self.selected_rgbs:
            diff = np.abs(rgb.astype(np.int16) - np.array(c, dtype=np.int16))
            mask |= np.all(diff <= tol, axis=-1)
        return mask
