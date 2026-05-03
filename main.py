import os
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from service.main_window import MainWindow, _resource_path


def main():
    # AppUserModelID : indispensable sous Windows pour que la barre des taches
    # affiche notre icone et pas celle de python.exe.
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("coloratio.app")
        except Exception:
            pass

    app = QApplication(sys.argv)
    icon_path = _resource_path("logo.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
