![banner](./banner.png)

<p align="center">
  <a href="https://github.com/Game-K-Hack/coloratio/releases/latest"><img src="https://img.shields.io/github/v/release/Game-K-Hack/coloratio?label=%E4%B8%8B%E8%BD%BD&style=for-the-badge&logo=windows" alt="下载"></a>
</p>

[:fr: Français](./README.fr.md) | 
[:uk: English](../README.md) | 
[:kr: 한국어](./README.ko.md) | 
[:jp: 日本語](./README.ja.md) | 
**:cn: 中文** | 
[:it: Italiano](./README.it.md) | 
[:es: Español](./README.es.md) | 
[:ru: Русский](./README.ru.md) | 
[:de: Deutsch](./README.de.md)

### Coloratio

**Coloratio** 是一款交互式桌面应用程序,可在保持视觉色调一致性的同时修改图像颜色。该应用程序会自动检测图像的主要颜色(量化调色板),允许您通过复选框选择一个或多个颜色,然后向目标颜色应用相对 HSV 偏移。所选颜色之间的比率得以保留:将一组蓝色移向绿色时,它们的相对色调保持不变。

Coloratio 基于 **PyQt5**、**Pillow** 和 **NumPy** 构建,支持高分辨率图像(预览自动缩小,保存时以全分辨率应用),并使用多线程在处理过程中保持 UI 流畅。

![schema](./screenshot.png)

---

### 安装

```
git clone https://github.com/Game-K-Hack/coloratio.git
cd coloratio
pip install -r requirements.txt
```

#### 启动图形界面

```
python main.py
```

#### 构建 EXE

```
pyinstaller --noconfirm build.spec
```
