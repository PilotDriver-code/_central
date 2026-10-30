"""Camada fina de compatibilidade: usa PySide6 e, se não houver, PyQt6.

Todo o resto do app importa Qt daqui, então trocar de binding não exige
mexer em nenhum outro arquivo.
"""

try:
    from PySide6 import QtCore, QtGui, QtWidgets, QtSvg  # noqa: F401

    Signal = QtCore.Signal
    Slot = QtCore.Slot
    Property = QtCore.Property
    BINDING = "PySide6"
except ImportError:  # pragma: no cover - fallback
    from PyQt6 import QtCore, QtGui, QtWidgets, QtSvg  # noqa: F401

    Signal = QtCore.pyqtSignal
    Slot = QtCore.pyqtSlot
    Property = QtCore.pyqtProperty
    BINDING = "PyQt6"

Qt = QtCore.Qt
