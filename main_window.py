"""Fenetre principale Coloratio."""

from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QSplitter, QScrollArea, QSlider, QColorDialog, QGroupBox,
    QAction, QMessageBox, QProgressBar, QSpinBox
)
from PyQt5.QtGui import QColor

from color_utils import pil_to_qpixmap, quantize_colors
from process_thread import ProcessThread
from widgets import ColorRow, ColorSwatch, ImageView


# Plafond de resolution pour le traitement temps-reel
WORK_MAX = 1600


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Coloratio")
        self.resize(1200, 800)

        self.original_img = None
        self.display_img = None
        self.modified_img = None
        self.color_rows = []
        self.target_rgb = (255, 255, 255)
        self.thread = None
        self.pending = False

        self._build_menu()
        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_menu(self):
        m = self.menuBar().addMenu("&Fichier")
        for label, sc, fn in [
            ("Ouvrir...", "Ctrl+O", self.open_image),
            ("Enregistrer sous...", "Ctrl+S", self.save_image),
        ]:
            a = QAction(label, self); a.setShortcut(sc); a.triggered.connect(fn)
            m.addAction(a)
        m.addSeparator()
        q = QAction("Quitter", self); q.triggered.connect(self.close)
        m.addAction(q)

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

        tol = QHBoxLayout()
        tol.addWidget(QLabel("Tolerance"))
        self.tol_slider = QSlider(Qt.Horizontal)
        self.tol_slider.setRange(0, 64); self.tol_slider.setValue(12)
        self.tol_slider.valueChanged.connect(lambda _: self._schedule_update())
        tol.addWidget(self.tol_slider)
        gl.addLayout(tol)
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
        selected = [r.rgb for r in self.color_rows if r.is_checked()]
        if not selected or self.original_img.size == self.display_img.size:
            return self.modified_img
        th = ProcessThread(self.original_img, selected,
                           self.target_rgb, self.tol_slider.value())
        result = {}
        th.finished_img.connect(lambda im: result.setdefault("img", im))
        th.run()  # synchrone : QThread.run direct
        return result.get("img", self.modified_img)

    # ------------------------------------------------------------- palette

    def _rebuild_palette(self):
        for r in self.color_rows:
            r.setParent(None)
        self.color_rows.clear()
        if self.display_img is None:
            return
        for rgb, count in quantize_colors(self.display_img, self.palette_spin.value()):
            row = ColorRow(rgb, count)
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
        selected = [r.rgb for r in self.color_rows if r.is_checked()]
        self.progress.show()
        self.thread = ProcessThread(self.display_img, selected,
                                    self.target_rgb, self.tol_slider.value())
        self.thread.finished_img.connect(self._on_processed)
        self.thread.start()

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
