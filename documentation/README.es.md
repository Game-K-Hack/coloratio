![banner](./banner.png)

<p align="center">
  <a href="https://github.com/Game-K-Hack/coloratio/releases/latest"><img src="https://img.shields.io/github/v/release/Game-K-Hack/coloratio?label=Descargar&style=for-the-badge&logo=windows" alt="Descargar"></a>
</p>

[:fr: Français](./README.fr.md) | 
[:uk: English](../README.md) | 
[:kr: 한국어](./README.ko.md) | 
[:jp: 日本語](./README.ja.md) | 
[:cn: 中文](./README.zh.md) | 
[:it: Italiano](./README.it.md) | 
**:es: Español** | 
[:ru: Русский](./README.ru.md) | 
[:de: Deutsch](./README.de.md)

### Coloratio

**Coloratio** es una aplicación de escritorio interactiva para modificar los colores de una imagen preservando la coherencia visual de los tonos. La aplicación detecta automáticamente los colores dominantes de tu imagen (paleta cuantizada), te permite seleccionar uno o varios mediante casillas de verificación y aplica un desplazamiento HSV relativo hacia un color objetivo. La proporción entre los colores seleccionados se conserva: al desplazar un grupo de azules hacia el verde, los matices relativos permanecen intactos.

Construida con **PyQt5**, **Pillow** y **NumPy**, Coloratio admite imágenes de alta resolución (redimensionamiento automático para la vista previa, aplicación a resolución completa al guardar) y utiliza multithreading para mantener la interfaz fluida durante el procesamiento.

![schema](./screenshot.png)

---

### Instalación

```
git clone https://github.com/Game-K-Hack/coloratio.git
cd coloratio
pip install -r requirements.txt
```

#### Lanzamiento de la interfaz gráfica

```
python main.py
```

#### Compilación a EXE

```
pyinstaller --noconfirm build.spec
```
