![banner](./banner.png)

<p align="center">
  <a href="https://github.com/Game-K-Hack/coloratio/releases/latest"><img src="https://img.shields.io/github/v/release/Game-K-Hack/coloratio?label=Herunterladen&style=for-the-badge&logo=windows" alt="Herunterladen"></a>
</p>

[:fr: Français](./README.fr.md) | 
[:uk: English](../README.md) | 
[:kr: 한국어](./README.ko.md) | 
[:jp: 日本語](./README.ja.md) | 
[:cn: 中文](./README.zh.md) | 
[:it: Italiano](./README.it.md) | 
[:es: Español](./README.es.md) | 
[:ru: Русский](./README.ru.md) | 
**:de: Deutsch**

### Coloratio

**Coloratio** ist eine interaktive Desktop-Anwendung zur Bearbeitung der Farben eines Bildes unter Beibehaltung der visuellen Farbtonkohärenz. Die Anwendung erkennt automatisch die dominanten Farben Ihres Bildes (quantisierte Palette), ermöglicht Ihnen die Auswahl einer oder mehrerer über Kontrollkästchen und wendet eine relative HSV-Verschiebung in Richtung einer Zielfarbe an. Das Verhältnis zwischen den ausgewählten Farben bleibt erhalten: Wenn Sie eine Gruppe von Blautönen in Richtung Grün verschieben, bleiben die relativen Schattierungen intakt.

Coloratio wurde mit **PyQt5**, **Pillow** und **NumPy** entwickelt und unterstützt hochauflösende Bilder (automatische Verkleinerung für die Vorschau, Anwendung in voller Auflösung beim Speichern) und nutzt Multithreading, um die Oberfläche während der Verarbeitung flüssig zu halten.

![schema](./screenshot.png)

---

### Installation

```
git clone https://github.com/Game-K-Hack/coloratio.git
cd coloratio
pip install -r requirements.txt
```

#### Starten der grafischen Oberfläche

```
python main.py
```

#### Erstellen der EXE

```
pyinstaller --noconfirm build.spec
```
