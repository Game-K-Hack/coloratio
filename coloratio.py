"""
Coloratio - Editeur de couleurs interactif
Application PyQt5 + PIL/NumPy permettant de selectionner des couleurs
dans une image et de les remplacer en conservant les ratios HSV
entre les couleurs selectionnees.
"""

import sys
import colorsys
from collections import Counter

import numpy as np
from PIL import Image

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QImage, QColor, QIcon, QPainter
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QSplitter, QScrollArea, QCheckBox,
    QSlider, QColorDialog, QGroupBox, QAction, QMessageBox, QFrame,
    QSizePolicy, QProgressBar, QSpinBox
)


# ---------------------------------------------------------------------------
# Utilitaires de conversion / quantification
# ---------------------------------------------------------------------------

def pil_to_qpixmap(pil_img: Image.Image) -> QPixmap:
    """Convertit une image PIL (RGB/RGBA) en QPixmap."""
    if pil_img.mode != "RGBA":
        pil_img = pil_img.convert("RGBA")
    data = pil_img.tobytes("raw", "RGBA")
    qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg.copy())


def quantize_colors(pil_img: Image.Image, max_colors: int = 32):
    """Retourne une liste [(r,g,b), count] des couleurs dominantes."""
    small = pil_img.convert("RGB")
    if max(small.size) > 400:
        small.thumbnail((400, 400))
    q = small.quantize(colors=max_colors, method=Image.Quantize.FASTOCTREE)
    palette = q.getpalette()[: max_colors * 3]
    counts = Counter(q.getdata())
    result = []
    for idx, count in counts.most_common():
        r, g, b = palette[idx * 3: idx * 3 + 3]
        result.append(((r, g, b), count))
    return result


def rgb_to_hsv_np(rgb: np.ndarray) -> np.ndarray:
    """Convertit un tableau (...,3) RGB [0..255] en HSV [0..1]."""
    arr = rgb.astype(np.float32) / 255.0
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    mx = np.max(arr, axis=-1)
    mn = np.min(arr, axis=-1)
    diff = mx - mn

    h = np.zeros_like(mx)
    mask = diff != 0
    rc = np.where(mask & (mx == r), ((g - b) / np.where(diff == 0, 1, diff)) % 6, 0)
    gc = np.where(mask & (mx == g), ((b - r) / np.where(diff == 0, 1, diff)) + 2, 0)
    bc = np.where(mask & (mx == b), ((r - g) / np.where(diff == 0, 1, diff)) + 4, 0)
    h = (rc + gc + bc) / 6.0
    h = h % 1.0

    s = np.where(mx == 0, 0, diff / np.where(mx == 0, 1, mx))
    v = mx
    return np.stack([h, s, v], axis=-1)


def hsv_to_rgb_np(hsv: np.ndarray) -> np.ndarray:
    """Convertit (...,3) HSV [0..1] en RGB [0..255] uint8."""
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
    rgb = np.stack([r, g, b], axis=-1)
    return np.clip(rgb * 255.0, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# Thread de traitement
# ---------------------------------------------------------------------------

class ProcessThread(QThread):
    """Applique le decalage HSV aux pixels selectionnes en arriere-plan."""

    finished_img = pyqtSignal(object)  # PIL.Image

    def __init__(self, base_img: Image.Image, selected_rgbs, target_rgb, tolerance):
        super().__init__()
        self.base_img = base_img
        self.selected_rgbs = selected_rgbs  # liste de tuples (r,g,b)
        self.target_rgb = target_rgb        # tuple (r,g,b)
        self.tolerance = tolerance          # int 0..64

    def run(self):
        if not self.selected_rgbs:
            self.finished_img.emit(self.base_img.copy())
            return

        img = self.base_img.convert("RGBA")
        arr = np.array(img)
        rgb = arr[..., :3]
        alpha = arr[..., 3:4]

        # Couleur de reference = moyenne des couleurs cochees (centre de gravite)
        sel = np.array(self.selected_rgbs, dtype=np.float32)
        ref_rgb = sel.mean(axis=0)
        ref_hsv = colorsys.rgb_to_hsv(*(ref_rgb / 255.0))
        target_hsv = colorsys.rgb_to_hsv(*(np.array(self.target_rgb) / 255.0))

        # Decalages HSV a appliquer (relatifs)
        dh = target_hsv[0] - ref_hsv[0]
        ds = target_hsv[1] - ref_hsv[1]
        dv = target_hsv[2] - ref_hsv[2]

        # Masque : pixels suffisamment proches d'au moins une couleur cochee
        tol = max(1, int(self.tolerance))
        mask = np.zeros(rgb.shape[:2], dtype=bool)
        for c in self.selected_rgbs:
            diff = np.abs(rgb.astype(np.int16) - np.array(c, dtype=np.int16))
            mask |= np.all(diff <= tol, axis=-1)

        if not mask.any():
            self.finished_img.emit(self.base_img.copy())
            return

        sub = rgb[mask]
        sub_hsv = rgb_to_hsv_np(sub)
        # Application relative : on conserve les ratios entre couleurs
        sub_hsv[..., 0] = (sub_hsv[..., 0] + dh) % 1.0
        sub_hsv[..., 1] = np.clip(sub_hsv[..., 1] + ds, 0.0, 1.0)
        sub_hsv[..., 2] = np.clip(sub_hsv[..., 2] + dv, 0.0, 1.0)
        new_rgb = hsv_to_rgb_np(sub_hsv)

        out = rgb.copy()
        out[mask] = new_rgb
        result = np.concatenate([out, alpha], axis=-1)
        self.finished_img.emit(Image.fromarray(result, mode="RGBA"))


# ---------------------------------------------------------------------------
# Widget : entree de couleur (carre + hex/rgb + checkbox)
# ---------------------------------------------------------------------------

class ColorRow(QWidget):
    def __init__(self, rgb, count, parent=None):
        super().__init__(parent)
        self.rgb = rgb
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        self.checkbox = QCheckBox()
        layout.addWidget(self.checkbox)

        swatch = QLabel()
        swatch.setFixedSize(QSize(28, 28))
        pix = QPixmap(28, 28)
        pix.fill(QColor(*rgb))
        swatch.setPixmap(pix)
        swatch.setFrameShape(QFrame.Box)
        layout.addWidget(swatch)

        hex_str = "#{:02X}{:02X}{:02X}".format(*rgb)
        info = QLabel(f"{hex_str}\nrgb{rgb}  ({count}px)")
        info.setStyleSheet("font-family: monospace; font-size: 10px;")
        layout.addWidget(info, 1)

    def is_checked(self):
        return self.checkbox.isChecked()


# ---------------------------------------------------------------------------
# Fenetre principale
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coloratio - editeur de couleurs")
        self.resize(1200, 800)

        self.original_img = None        # PIL Image originale (pleine resolution)
        self.display_img = None         # version eventuellement reduite pour traitement
        self.modified_img = None        # resultat actuel
        self.color_rows = []            # liste des ColorRow
        self.target_rgb = (255, 255, 255)
        self.thread = None
        self.pending = False            # une autre maj est demandee

        self._build_menu()
        self._build_ui()

    # ----- UI ---------------------------------------------------------------

    def _build_menu(self):
        bar = self.menuBar()
        file_menu = bar.addMenu("&Fichier")

        open_act = QAction("Ouvrir...", self)
        open_act.setShortcut("Ctrl+O")
        open_act.triggered.connect(self.open_image)
        file_menu.addAction(open_act)

        save_act = QAction("Enregistrer sous...", self)
        save_act.setShortcut("Ctrl+S")
        save_act.triggered.connect(self.save_image)
        file_menu.addAction(save_act)

        file_menu.addSeparator()
        quit_act = QAction("Quitter", self)
        quit_act.triggered.connect(self.close)
        file_menu.addAction(quit_act)

    def _build_ui(self):
        splitter = QSplitter(Qt.Horizontal)

        # ---- Panneau gauche : liste des couleurs + controles cible --------
        left = QWidget()
        left_layout = QVBoxLayout(left)

        title = QLabel("Couleurs detectees")
        title.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(title)

        # Nombre max de couleurs quantifiees
        qbox = QHBoxLayout()
        qbox.addWidget(QLabel("Palette :"))
        self.palette_spin = QSpinBox()
        self.palette_spin.setRange(2, 128)
        self.palette_spin.setValue(24)
        self.palette_spin.valueChanged.connect(self._rebuild_palette)
        qbox.addWidget(self.palette_spin)
        qbox.addStretch(1)
        left_layout.addLayout(qbox)

        self.color_scroll = QScrollArea()
        self.color_scroll.setWidgetResizable(True)
        self.color_container = QWidget()
        self.color_layout = QVBoxLayout(self.color_container)
        self.color_layout.setAlignment(Qt.AlignTop)
        self.color_scroll.setWidget(self.color_container)
        left_layout.addWidget(self.color_scroll, 1)

        # Selection rapide
        sel_btns = QHBoxLayout()
        b_all = QPushButton("Tout cocher")
        b_all.clicked.connect(lambda: self._set_all_checked(True))
        b_none = QPushButton("Tout decocher")
        b_none.clicked.connect(lambda: self._set_all_checked(False))
        sel_btns.addWidget(b_all)
        sel_btns.addWidget(b_none)
        left_layout.addLayout(sel_btns)

        # ---- Couleur cible -------------------------------------------------
        target_group = QGroupBox("Couleur cible")
        tg_layout = QVBoxLayout(target_group)

        self.target_swatch = QLabel()
        self.target_swatch.setFixedHeight(40)
        self.target_swatch.setFrameShape(QFrame.Box)
        self._refresh_target_swatch()
        tg_layout.addWidget(self.target_swatch)

        pick_btn = QPushButton("Choisir avec la palette...")
        pick_btn.clicked.connect(self._pick_color_dialog)
        tg_layout.addWidget(pick_btn)

        # Sliders RGB
        self.sliders = {}
        for name in ("R", "G", "B"):
            row = QHBoxLayout()
            row.addWidget(QLabel(name))
            s = QSlider(Qt.Horizontal)
            s.setRange(0, 255)
            s.setValue(255)
            s.valueChanged.connect(self._on_slider_changed)
            row.addWidget(s)
            val = QLabel("255")
            val.setFixedWidth(30)
            row.addWidget(val)
            tg_layout.addLayout(row)
            self.sliders[name] = (s, val)

        # Tolerance
        tol_row = QHBoxLayout()
        tol_row.addWidget(QLabel("Tolerance"))
        self.tol_slider = QSlider(Qt.Horizontal)
        self.tol_slider.setRange(0, 64)
        self.tol_slider.setValue(12)
        self.tol_slider.valueChanged.connect(lambda _: self._schedule_update())
        tol_row.addWidget(self.tol_slider)
        tg_layout.addLayout(tol_row)

        left_layout.addWidget(target_group)

        # ---- Panneau droit : image -----------------------------------------
        right = QWidget()
        right_layout = QVBoxLayout(right)
        self.image_label = QLabel("Aucune image chargee")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setStyleSheet("background:#222; color:#aaa;")
        right_layout.addWidget(self.image_label, 1)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        right_layout.addWidget(self.progress)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([380, 820])

        self.setCentralWidget(splitter)

    # ----- Gestion image ---------------------------------------------------

    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir une image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.webp)"
        )
        if not path:
            return
        try:
            img = Image.open(path).convert("RGBA")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir : {e}")
            return

        self.original_img = img
        # Pour le traitement, on garde une version raisonnable (max 1600px)
        work = img.copy()
        if max(work.size) > 1600:
            work.thumbnail((1600, 1600), Image.LANCZOS)
        self.display_img = work
        self.modified_img = work.copy()

        self._rebuild_palette()
        self._refresh_image_view()

    def save_image(self):
        if self.modified_img is None:
            QMessageBox.information(self, "Info", "Aucune image a enregistrer.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer sous", "",
            "PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp)"
        )
        if not path:
            return
        try:
            # Si l'original etait plus grand, on applique aussi sur l'original
            # via le meme thread synchronement pour preserver la resolution.
            if self.original_img.size != self.display_img.size:
                selected = [r.rgb for r in self.color_rows if r.is_checked()]
                if selected:
                    th = ProcessThread(self.original_img, selected,
                                       self.target_rgb, self.tol_slider.value())
                    th.run()  # synchrone : on attend
                    # th.finished_img est emis avant retour de run(); recuperer via attribut
                    out = self._sync_result if hasattr(self, "_sync_result") else self.modified_img
                else:
                    out = self.original_img
            else:
                out = self.modified_img

            if path.lower().endswith((".jpg", ".jpeg")):
                out.convert("RGB").save(path, quality=95)
            else:
                out.save(path)
            QMessageBox.information(self, "OK", "Image enregistree.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Echec : {e}")

    # ----- Palette ---------------------------------------------------------

    def _rebuild_palette(self):
        # Vider l'ancienne liste
        for r in self.color_rows:
            r.setParent(None)
        self.color_rows.clear()
        if self.display_img is None:
            return
        colors = quantize_colors(self.display_img, self.palette_spin.value())
        for rgb, count in colors:
            row = ColorRow(rgb, count)
            row.checkbox.stateChanged.connect(lambda _: self._schedule_update())
            self.color_layout.addWidget(row)
            self.color_rows.append(row)

    def _set_all_checked(self, val: bool):
        for r in self.color_rows:
            r.checkbox.blockSignals(True)
            r.checkbox.setChecked(val)
            r.checkbox.blockSignals(False)
        self._schedule_update()

    # ----- Couleur cible ---------------------------------------------------

    def _refresh_target_swatch(self):
        pix = QPixmap(self.target_swatch.size() if self.target_swatch.width() > 1 else QSize(200, 40))
        pix.fill(QColor(*self.target_rgb))
        self.target_swatch.setPixmap(pix)

    def _pick_color_dialog(self):
        c = QColorDialog.getColor(QColor(*self.target_rgb), self, "Couleur cible")
        if c.isValid():
            self.target_rgb = (c.red(), c.green(), c.blue())
            for name, val in zip("RGB", self.target_rgb):
                s, lab = self.sliders[name]
                s.blockSignals(True); s.setValue(val); s.blockSignals(False)
                lab.setText(str(val))
            self._refresh_target_swatch()
            self._schedule_update()

    def _on_slider_changed(self, _):
        vals = []
        for name in "RGB":
            s, lab = self.sliders[name]
            v = s.value()
            lab.setText(str(v))
            vals.append(v)
        self.target_rgb = tuple(vals)
        self._refresh_target_swatch()
        self._schedule_update()

    # ----- Traitement ------------------------------------------------------

    def _schedule_update(self):
        if self.display_img is None:
            return
        if self.thread and self.thread.isRunning():
            self.pending = True
            return
        self._launch_thread()

    def _launch_thread(self):
        selected = [r.rgb for r in self.color_rows if r.is_checked()]
        self.progress.show()
        self.thread = ProcessThread(self.display_img, selected,
                                    self.target_rgb, self.tol_slider.value())
        self.thread.finished_img.connect(self._on_processed)
        self.thread.start()

    def _on_processed(self, img):
        self.modified_img = img
        self._sync_result = img
        self._refresh_image_view()
        self.progress.hide()
        if self.pending:
            self.pending = False
            self._launch_thread()

    def _refresh_image_view(self):
        if self.modified_img is None:
            return
        pix = pil_to_qpixmap(self.modified_img)
        target = self.image_label.size()
        if target.width() > 10 and target.height() > 10:
            pix = pix.scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pix)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._refresh_image_view()


# ---------------------------------------------------------------------------
# Entree
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
