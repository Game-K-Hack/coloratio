![banner](./banner.png)

<p align="center">
  <a href="https://github.com/Game-K-Hack/coloratio/releases/latest"><img src="https://img.shields.io/github/v/release/Game-K-Hack/coloratio?label=T%C3%A9l%C3%A9charger&style=for-the-badge&logo=windows" alt="Télécharger"></a>
</p>

**:fr: Français** | 
[:uk: English](../README.md) | 
[:kr: 한국어](./README.ko.md) | 
[:jp: 日本語](./README.ja.md) | 
[:cn: 中文](./README.zh.md) | 
[:it: Italiano](./README.it.md) | 
[:es: Español](./README.es.md) | 
[:ru: Русский](./README.ru.md) | 
[:de: Deutsch](./README.de.md)

### Coloratio

**Coloratio** est une application de bureau interactive permettant de modifier les couleurs d'une image en conservant la cohérence visuelle des teintes. L'application détecte automatiquement les couleurs dominantes de votre image (palette quantifiée), vous laisse en sélectionner une ou plusieurs via des cases à cocher, puis applique un décalage HSV relatif vers une couleur cible. Le ratio entre les couleurs sélectionnées est préservé : si vous décalez la teinte d'un groupe de bleus vers du vert, les nuances restent proportionnelles entre elles.

Construite avec **PyQt5**, **Pillow** et **NumPy**, Coloratio prend en charge les images haute résolution (redimensionnement automatique pour l'aperçu, application pleine résolution à la sauvegarde) et utilise le multithreading pour garder l'interface fluide pendant le traitement.

![schema](./screenshot.png)

---

### Installation

```
git clone https://github.com/Game-K-Hack/coloratio.git
cd coloratio
pip install -r requirements.txt
```

#### Lancement de l'interface graphique

```
python main.py
```

#### Build en EXE

```
pyinstaller --noconfirm build.spec
```
