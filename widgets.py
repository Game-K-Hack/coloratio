from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QColor, QPainter
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox, QFrame, QSizePolicy


class ColorRow(QWidget):
    """Ligne palette : checkbox + swatch + texte HEX/RGB."""

    def __init__(self, rgb, count, index=-1, parent=None):
        super().__init__(parent)
        self.rgb = rgb
        self.index = index
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


class ColorSwatch(QFrame):
    """Aperçu de couleur a hauteur fixe : ne fait jamais grandir le layout."""

    def __init__(self, rgb=(255, 255, 255), parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Box)
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._color = QColor(*rgb)

    def set_color(self, rgb):
        self._color = QColor(*rgb)
        self.update()

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self)
        p.fillRect(self.rect().adjusted(1, 1, -1, -1), self._color)


class ImageView(QFrame):
    """
    Affiche un QPixmap rescale (ratio conserve) sans propager
    sa sizeHint au parent. C'est ce qui evitait l'agrandissement
    de l'interface a chaque mise a jour.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        # Politique "Ignored" : la taille demandee n'influence pas le layout.
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setMinimumSize(1, 1)
        self.setStyleSheet("background:#222;")
        self._pixmap = None
        self._placeholder = "Aucune image chargee"

    def sizeHint(self):
        return QSize(400, 400)

    def minimumSizeHint(self):
        return QSize(1, 1)

    def set_pixmap(self, pix: QPixmap):
        self._pixmap = pix
        self.update()

    def clear(self):
        self._pixmap = None
        self.update()

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self)
        p.fillRect(self.rect(), Qt.black)
        if self._pixmap is None or self._pixmap.isNull():
            p.setPen(Qt.lightGray)
            p.drawText(self.rect(), Qt.AlignCenter, self._placeholder)
            return
        scaled = self._pixmap.scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        p.drawPixmap(x, y, scaled)
