import sys

from app.qt import QtGui, QtWidgets
from app.window import MainWindow


def main() -> int:
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Central Eventos RF")
    app.setStyle("Fusion")  # base neutra e igual em qualquer Windows

    font = QtGui.QFont()
    font.setFamilies(["Segoe UI Variable Text", "Segoe UI", "Inter", "Roboto"])
    font.setPointSize(10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
