![banner](./banner.png)

<p align="center">
  <a href="https://github.com/Game-K-Hack/coloratio/releases/latest"><img src="https://img.shields.io/github/v/release/Game-K-Hack/coloratio?label=%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89&style=for-the-badge&logo=windows" alt="ダウンロード"></a>
</p>

[:fr: Français](./README.fr.md) | 
[:uk: English](../README.md) | 
[:kr: 한국어](./README.ko.md) | 
**:jp: 日本語** | 
[:cn: 中文](./README.zh.md) | 
[:it: Italiano](./README.it.md) | 
[:es: Español](./README.es.md) | 
[:ru: Русский](./README.ru.md) | 
[:de: Deutsch](./README.de.md)

### Coloratio

**Coloratio**は、画像の色調の一貫性を保ちながらインタラクティブに色を編集できるデスクトップアプリケーションです。画像の主要な色(量子化されたパレット)を自動的に検出し、チェックボックスで1つまたは複数を選択し、ターゲット色への相対的なHSVシフトを適用します。選択された色間の比率は保持されます:青のグループを緑にシフトすると、相対的な色合いはそのまま維持されます。

**PyQt5**、**Pillow**、**NumPy**で構築されたColoratioは、高解像度画像に対応し(プレビューは縮小、保存時はフル解像度で適用)、マルチスレッドを使用して処理中もUIをスムーズに保ちます。

![schema](./screenshot.png)

---

### インストール

```
git clone https://github.com/Game-K-Hack/coloratio.git
cd coloratio
pip install -r requirements.txt
```

#### GUIの起動

```
python main.py
```

#### EXEのビルド

```
pyinstaller --noconfirm build.spec
```
