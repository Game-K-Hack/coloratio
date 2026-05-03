![banner](./banner.png)

<p align="center">
  <a href="https://github.com/Game-K-Hack/coloratio/releases/latest"><img src="https://img.shields.io/github/v/release/Game-K-Hack/coloratio?label=%EB%8B%A4%EC%9A%B4%EB%A1%9C%EB%93%9C&style=for-the-badge&logo=windows" alt="다운로드"></a>
</p>

[:fr: Français](./README.fr.md) | 
[:uk: English](../README.md) | 
**:kr: 한국어** | 
[:jp: 日本語](./README.ja.md) | 
[:cn: 中文](./README.zh.md) | 
[:it: Italiano](./README.it.md) | 
[:es: Español](./README.es.md) | 
[:ru: Русский](./README.ru.md) | 
[:de: Deutsch](./README.de.md)

### Coloratio

**Coloratio**는 이미지의 색조 일관성을 유지하면서 색상을 대화식으로 수정할 수 있는 데스크톱 애플리케이션입니다. 이미지의 주요 색상(양자화된 팔레트)을 자동으로 감지하고, 체크박스를 통해 하나 이상의 색상을 선택한 다음, 대상 색상으로 상대적인 HSV 변환을 적용합니다. 선택된 색상 간의 비율은 유지됩니다: 파란색 그룹을 녹색으로 이동하면 상대적인 음영이 그대로 유지됩니다.

**PyQt5**, **Pillow**, **NumPy**로 구축된 Coloratio는 고해상도 이미지를 지원하며 (미리보기는 축소, 저장 시 전체 해상도 적용), 멀티스레딩을 사용하여 처리 중에도 UI가 부드럽게 유지됩니다.

![schema](./screenshot.png)

---

### 설치

```
git clone https://github.com/Game-K-Hack/coloratio.git
cd coloratio
pip install -r requirements.txt
```

#### GUI 실행

```
python main.py
```

#### EXE 빌드

```
pyinstaller --noconfirm build.spec
```
