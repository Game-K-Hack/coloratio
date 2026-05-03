![banner](./banner.png)

<p align="center">
  <a href="https://github.com/Game-K-Hack/coloratio/releases/latest"><img src="https://img.shields.io/github/v/release/Game-K-Hack/coloratio?label=Scarica&style=for-the-badge&logo=windows" alt="Scarica"></a>
</p>

[:fr: Français](./README.fr.md) | 
[:uk: English](../README.md) | 
[:kr: 한국어](./README.ko.md) | 
[:jp: 日本語](./README.ja.md) | 
[:cn: 中文](./README.zh.md) | 
**:it: Italiano** | 
[:es: Español](./README.es.md) | 
[:ru: Русский](./README.ru.md) | 
[:de: Deutsch](./README.de.md)

### Coloratio

**Coloratio** è un'applicazione desktop interattiva per modificare i colori di un'immagine preservando la coerenza visiva delle tonalità. L'applicazione rileva automaticamente i colori dominanti dell'immagine (palette quantizzata), consente di selezionarne uno o più tramite caselle di controllo, quindi applica uno spostamento HSV relativo verso un colore target. Il rapporto tra i colori selezionati viene preservato: spostando un gruppo di blu verso il verde, le sfumature relative restano intatte.

Costruita con **PyQt5**, **Pillow** e **NumPy**, Coloratio supporta immagini ad alta risoluzione (ridimensionamento automatico per l'anteprima, applicazione a piena risoluzione al salvataggio) e utilizza il multithreading per mantenere fluida l'interfaccia durante l'elaborazione.

![schema](./screenshot.png)

---

### Installazione

```
git clone https://github.com/Game-K-Hack/coloratio.git
cd coloratio
pip install -r requirements.txt
```

#### Avvio dell'interfaccia grafica

```
python main.py
```

#### Compilazione in EXE

```
pyinstaller --noconfirm build.spec
```
