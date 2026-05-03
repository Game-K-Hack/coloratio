![banner](./documentation/banner.png)

<p align="center">
  <a href="https://github.com/Game-K-Hack/coloratio/releases/latest"><img src="https://img.shields.io/github/v/release/Game-K-Hack/coloratio?label=Download&style=for-the-badge&logo=windows" alt="Download"></a>
</p>

[:fr: Français](./documentation/README.fr.md) | 
**:uk: English** | 
[:kr: 한국어](./documentation/README.ko.md) | 
[:jp: 日本語](./documentation/README.ja.md) | 
[:cn: 中文](./documentation/README.zh.md) | 
[:it: Italiano](./documentation/README.it.md) | 
[:es: Español](./documentation/README.es.md) | 
[:ru: Русский](./documentation/README.ru.md) | 
[:de: Deutsch](./documentation/README.de.md)

### Coloratio

**Coloratio** is an interactive desktop application for editing the colors of an image while preserving visual hue consistency. The app automatically detects the dominant colors in your image (quantized palette), lets you select one or several via checkboxes, then applies a relative HSV shift toward a target color. Ratios between selected colors are preserved: shifting a group of blues toward green keeps their relative shades intact.

Built with **PyQt5**, **Pillow**, and **NumPy**, Coloratio handles high-resolution images (downscaled preview, full-resolution rendering on save) and uses multithreading to keep the UI responsive during processing.

![schema](./documentation/screenshot.png)

---

### Installation

```
git clone https://github.com/Game-K-Hack/coloratio.git
cd coloratio
pip install -r requirements.txt
```

#### Launching the GUI

```
python main.py
```

#### Building the EXE

```
pyinstaller --noconfirm build.spec
```
