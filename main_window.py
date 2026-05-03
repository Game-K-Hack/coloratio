import os
import sys
from PIL import Image
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QPixmap
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QSplitter, QScrollArea, QSlider, QColorDialog, QGroupBox,
    QAction, QMessageBox, QProgressBar, QSpinBox, QComboBox)
from PyQt5.QtGui import QColor, QIcon, QDesktopServices, QPixmap

APP_NAME = "Coloratio"
APP_VERSION = "0.1.0"
APP_AUTHOR = "Harlock"
APP_GITHUB = "https://github.com/Game-K-Hack/coloration"


def _resource_path(name: str) -> str:
    """Resout un fichier ressource en mode dev ou dans un EXE PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)

from color_utils import pil_to_qpixmap, quantize_full
from process_thread import ProcessThread
from widgets import ColorRow, ColorSwatch, ImageView


# Plafond de resolution pour le traitement temps-reel
WORK_MAX = 1600


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coloratio")
        self.resize(1200, 800)
        self.setMinimumSize(1200, 800)
        icon_path = _resource_path("logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.original_img = None
        self.display_img = None
        self.modified_img = None
        self.color_rows = []
        self.target_rgb = (255, 255, 255)
        self.thread = None
        self.pending = False
        # Carte d'indices palette pour l'image de travail
        self.index_map = None
        self.palette = []

        self._build_menu()
        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_menu(self):
        bar = self.menuBar()

        m = bar.addMenu("&Fichier")
        for label, sc, fn in [
            ("Ouvrir...", "Ctrl+O", self.open_image),
            ("Enregistrer sous...", "Ctrl+S", self.save_image),
        ]:
            a = QAction(label, self); a.setShortcut(sc); a.triggered.connect(fn)
            m.addAction(a)
        m.addSeparator()
        q = QAction("Quitter", self); q.triggered.connect(self.close)
        m.addAction(q)

        h = bar.addMenu("&Aide")
        doc = QAction("Documentation", self)
        doc.setShortcut("F1")
        doc.triggered.connect(self._open_documentation)
        h.addAction(doc)
        about = QAction("A propos", self)
        about.triggered.connect(self._show_about)
        h.addAction(about)

    def _open_documentation(self):
        QDesktopServices.openUrl(QUrl(APP_GITHUB))

    def _show_about(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(f"A propos de {APP_NAME}")
        icon_path = _resource_path("logo.ico")
        if os.path.exists(icon_path):
            pix = QPixmap(icon_path).scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            dlg.setIconPixmap(pix)
        dlg.setTextFormat(Qt.RichText)
        dlg.setText(
            f"<h2>{APP_NAME}</h2>"
            f"<p><b>Version :</b> {APP_VERSION}<br>"
            f"<b>Auteur :</b> {APP_AUTHOR}</p>"
            f"<p>Editeur de couleurs interactif base sur PyQt5, "
            f"Pillow et NumPy.</p>"
            f"<p><a href=\"{APP_GITHUB}\">{APP_GITHUB}</a></p>"
        )
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.exec_()

    def _build_ui(self):
        splitter = QSplitter(Qt.Horizontal)

        # -- gauche --
        left = QWidget()
        left.setMinimumWidth(320)
        left.setMaximumWidth(520)
        ll = QVBoxLayout(left)

        title = QLabel("Couleurs detectees")
        title.setStyleSheet("font-weight:bold;")
        ll.addWidget(title)

        qbox = QHBoxLayout()
        qbox.addWidget(QLabel("Palette :"))
        self.palette_spin = QSpinBox()
        self.palette_spin.setRange(2, 128)
        self.palette_spin.setValue(24)
        self.palette_spin.valueChanged.connect(self._rebuild_palette)
        qbox.addWidget(self.palette_spin)
        qbox.addStretch(1)
        ll.addLayout(qbox)

        self.color_scroll = QScrollArea()
        self.color_scroll.setWidgetResizable(True)
        self.color_container = QWidget()
        self.color_layout = QVBoxLayout(self.color_container)
        self.color_layout.setAlignment(Qt.AlignTop)
        self.color_scroll.setWidget(self.color_container)
        ll.addWidget(self.color_scroll, 1)

        sel = QHBoxLayout()
        b1 = QPushButton("Tout cocher"); b1.clicked.connect(lambda: self._set_all(True))
        b2 = QPushButton("Tout decocher"); b2.clicked.connect(lambda: self._set_all(False))
        sel.addWidget(b1); sel.addWidget(b2)
        ll.addLayout(sel)

        # cible
        grp = QGroupBox("Couleur cible")
        gl = QVBoxLayout(grp)
        self.target_swatch = ColorSwatch(self.target_rgb)
        gl.addWidget(self.target_swatch)

        pick = QPushButton("Choisir avec la palette...")
        pick.clicked.connect(self._pick_color_dialog)
        gl.addWidget(pick)

        self.sliders = {}
        for name in ("R", "G", "B"):
            row = QHBoxLayout()
            row.addWidget(QLabel(name))
            s = QSlider(Qt.Horizontal); s.setRange(0, 255); s.setValue(255)
            s.valueChanged.connect(self._on_slider_changed)
            row.addWidget(s)
            v = QLabel("255"); v.setFixedWidth(30)
            row.addWidget(v)
            gl.addLayout(row)
            self.sliders[name] = (s, v)

        # Mode de masque
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Masque"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Cluster palette (tous les pixels)", "index")
        self.mode_combo.addItem("Tolerance RGB", "tolerance")
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_row.addWidget(self.mode_combo, 1)
        gl.addLayout(mode_row)

        tol = QHBoxLayout()
        self.tol_label = QLabel("Tolerance")
        tol.addWidget(self.tol_label)
        self.tol_slider = QSlider(Qt.Horizontal)
        self.tol_slider.setRange(0, 64); self.tol_slider.setValue(12)
        self.tol_slider.valueChanged.connect(lambda _: self._schedule_update())
        tol.addWidget(self.tol_slider)
        gl.addLayout(tol)
        self._update_tolerance_enabled()
        ll.addWidget(grp)

        # -- droite --
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        self.image_view = ImageView()
        rl.addWidget(self.image_view, 1)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(8)
        self.progress.hide()
        rl.addWidget(self.progress)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([360, 840])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        self.setCentralWidget(splitter)

    # -------------------------------------------------------------- image

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
        work = img.copy()
        if max(work.size) > WORK_MAX:
            work.thumbnail((WORK_MAX, WORK_MAX), Image.LANCZOS)
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
            out = self._render_full_resolution()
            if path.lower().endswith((".jpg", ".jpeg")):
                out.convert("RGB").save(path, quality=95)
            else:
                out.save(path)
            QMessageBox.information(self, "OK", "Image enregistree.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Echec : {e}")

    def _render_full_resolution(self):
        """Reapplique la transformation sur l'originale pleine resolution."""
        selected_rows = [r for r in self.color_rows if r.is_checked()]
        if not selected_rows or self.original_img.size == self.display_img.size:
            return self.modified_img

        selected = [r.rgb for r in selected_rows]
        indices = [r.index for r in selected_rows]
        mode = self.mode_combo.currentData()
        full_index_map = None
        if mode == "index":
            full_index_map, _, _ = quantize_full(
                self.original_img, self.palette_spin.value()
            )
        th = ProcessThread(
            self.original_img, selected, self.target_rgb,
            mode=mode, tolerance=self.tol_slider.value(),
            index_map=full_index_map, selected_indices=indices,
        )
        result = {}
        th.finished_img.connect(lambda im: result.setdefault("img", im))
        th.run()
        return result.get("img", self.modified_img)

    # ------------------------------------------------------------- palette

    def _rebuild_palette(self):
        for r in self.color_rows:
            r.setParent(None)
        self.color_rows.clear()
        if self.display_img is None:
            return
        # Quantifie l'image ENTIERE -> chaque pixel a un index palette
        self.index_map, self.palette, counts = quantize_full(
            self.display_img, self.palette_spin.value()
        )
        for idx, (rgb, count) in enumerate(zip(self.palette, counts)):
            row = ColorRow(rgb, count, index=idx)
            row.checkbox.stateChanged.connect(lambda _: self._schedule_update())
            self.color_layout.addWidget(row)
            self.color_rows.append(row)

    def _set_all(self, val):
        for r in self.color_rows:
            r.checkbox.blockSignals(True)
            r.checkbox.setChecked(val)
            r.checkbox.blockSignals(False)
        self._schedule_update()

    # ----------------------------------------------------------- target

    def _pick_color_dialog(self):
        c = QColorDialog.getColor(QColor(*self.target_rgb), self, "Couleur cible")
        if not c.isValid():
            return
        self.target_rgb = (c.red(), c.green(), c.blue())
        for n, val in zip("RGB", self.target_rgb):
            s, lab = self.sliders[n]
            s.blockSignals(True); s.setValue(val); s.blockSignals(False)
            lab.setText(str(val))
        self.target_swatch.set_color(self.target_rgb)
        self._schedule_update()

    def _on_slider_changed(self, _):
        vals = []
        for n in "RGB":
            s, lab = self.sliders[n]
            v = s.value(); lab.setText(str(v)); vals.append(v)
        self.target_rgb = tuple(vals)
        self.target_swatch.set_color(self.target_rgb)
        self._schedule_update()

    # ---------------------------------------------------------- threading

    def _schedule_update(self):
        if self.display_img is None:
            return
        if self.thread and self.thread.isRunning():
            self.pending = True
            return
        self._launch_thread()

    def _launch_thread(self):
        selected_rows = [r for r in self.color_rows if r.is_checked()]
        selected = [r.rgb for r in selected_rows]
        indices = [r.index for r in selected_rows]
        mode = self.mode_combo.currentData()
        self.progress.show()
        self.thread = ProcessThread(
            self.display_img, selected, self.target_rgb,
            mode=mode, tolerance=self.tol_slider.value(),
            index_map=self.index_map, selected_indices=indices,
        )
        self.thread.finished_img.connect(self._on_processed)
        self.thread.start()

    def _on_mode_changed(self, _):
        self._update_tolerance_enabled()
        self._schedule_update()

    def _update_tolerance_enabled(self):
        is_tol = self.mode_combo.currentData() == "tolerance"
        self.tol_slider.setEnabled(is_tol)
        self.tol_label.setEnabled(is_tol)

    def _on_processed(self, img):
        self.modified_img = img
        self._refresh_image_view()
        self.progress.hide()
        if self.pending:
            self.pending = False
            self._launch_thread()

    def _refresh_image_view(self):
        if self.modified_img is None:
            self.image_view.clear()
            return
        self.image_view.set_pixmap(pil_to_qpixmap(self.modified_img))
