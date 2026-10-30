"""Tema da aplicação: tokens de cor + folha de estilo (QSS) gerada a partir deles.

Para ajustar cores, mexa só nos dicionários LIGHT / DARK. O QSS inteiro é
montado a partir desses tokens, então não existe cor "solta" no código.
"""

import os
import tempfile
from string import Template

from . import icons

MONO = '"Cascadia Mono", "Consolas", "JetBrains Mono", "DejaVu Sans Mono", monospace'
SANS = '"Segoe UI Variable Text", "Segoe UI", "Inter", "Roboto", sans-serif'

# Cores do console de execução: sempre escuro, nos dois temas.
_CONSOLE = {
    "con_bg": "#050B22",
    "con_border": "#141E45",
    "con_text": "#D3D8EA",
    "con_muted": "#69739A",
    "con_info": "#86A8FF",
    "con_ok": "#45D99A",
    "con_warn": "#FFB547",
    "con_error": "#FF7474",
}

LIGHT = {
    "canvas": "#EEF1F6",
    "surface": "#FFFFFF",
    "field": "#F6F7FA",
    "hover": "#E8EBF2",
    "border": "#DCE0EA",
    "border_strong": "#C3C9D9",
    "ink": "#0A1433",
    "ink_muted": "#58627F",
    "ink_faint": "#8B93AB",
    "disabled_bg": "#E3E6EE",
    "sidebar": "#000D3C",
    "sidebar_hover": "#0A1A55",
    "sidebar_active": "#122463",
    "sidebar_text": "#97A1C2",
    "sidebar_line": "#1A2A63",
    "accent": "#FF6200",
    "accent_hover": "#EB5A00",
    "accent_pressed": "#CC4E00",
    "accent_soft": "#FFF0E5",
    "accent_text": "#C24700",
    "focus": "#2F5BEA",
    "success": "#178A5B",
    "success_soft": "#E2F5EC",
    "warn": "#A86200",
    "warn_soft": "#FFF3DC",
    "danger": "#C93434",
    "danger_soft": "#FCE8E8",
    **_CONSOLE,
}

DARK = {
    "canvas": "#070C21",
    "surface": "#0E1532",
    "field": "#121A3B",
    "hover": "#18214A",
    "border": "#1F2A52",
    "border_strong": "#2E3B6B",
    "ink": "#E7EAF4",
    "ink_muted": "#A1A9C6",
    "ink_faint": "#6D7698",
    "disabled_bg": "#1A2347",
    "sidebar": "#020821",
    "sidebar_hover": "#0C1640",
    "sidebar_active": "#152252",
    "sidebar_text": "#8E98BC",
    "sidebar_line": "#121C45",
    "accent": "#FF6200",
    "accent_hover": "#FF7424",
    "accent_pressed": "#E05600",
    "accent_soft": "#2B1A10",
    "accent_text": "#FF9150",
    "focus": "#6F8DFF",
    "success": "#45D99A",
    "success_soft": "#0F2E24",
    "warn": "#FFB547",
    "warn_soft": "#33250E",
    "danger": "#FF7474",
    "danger_soft": "#361519",
    **_CONSOLE,
}

_state = {"name": "light", "tokens": LIGHT}


def current() -> dict:
    return _state["tokens"]


def name() -> str:
    return _state["name"]


def set_theme(theme_name: str) -> dict:
    _state["name"] = "dark" if theme_name == "dark" else "light"
    _state["tokens"] = DARK if _state["name"] == "dark" else LIGHT
    return _state["tokens"]


def _svg_asset(icon_name: str, color: str) -> str:
    """Grava um SVG colorido em disco (QSS só aceita imagens por caminho)."""
    folder = os.path.join(tempfile.gettempdir(), "central_rf_icons")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{icon_name}_{color.strip('#')}.svg")
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(icons.svg(icon_name, color, 2))
    return path.replace("\\", "/")


_QSS = Template(r"""
* { font-family: $sans; }
QWidget { color: $ink; font-size: 13px; }
#Content { background: $canvas; }

/* Menu lateral ------------------------------------------------------- */
#Sidebar { background: $sidebar; }
#BrandName { color: #FFFFFF; font-size: 14px; font-weight: 600; }
#BrandSub { color: $sidebar_text; font-size: 12px; }
#NavSep { background: $sidebar_line; min-height: 1px; max-height: 1px; }
#NavButton {
    background: transparent; color: $sidebar_text; border: none;
    border-radius: 8px; padding: 0 10px; text-align: left; font-size: 13px;
}
#NavButton:hover { background: $sidebar_hover; color: #FFFFFF; }
#NavButton:checked { background: $sidebar_active; color: #FFFFFF; font-weight: 600; }

/* Cabeçalho ---------------------------------------------------------- */
#PageTitle { font-size: 22px; font-weight: 600; color: $ink; }
#PageDesc { font-size: 13px; color: $ink_muted; }
#Shortcut { font-size: 11px; color: $ink_faint; }

/* Painéis e campos --------------------------------------------------- */
#Panel { background: $surface; border: 1px solid $border; border-radius: 12px; }
#PanelTitle { font-size: 14px; font-weight: 600; color: $ink; }
#FieldLabel { font-size: 12px; font-weight: 600; color: $ink_muted; }
#Hint { font-size: 12px; color: $ink_faint; }
#Hint[tone="ok"] { color: $success; }
#Hint[tone="error"] { color: $danger; }
#Divider { background: $border; min-height: 1px; max-height: 1px; }
#StatValue { font-size: 20px; font-weight: 600; color: $ink; }
#Mono { font-family: $mono; font-size: 12px; color: $ink_muted; }

QLineEdit, QDateEdit, QPlainTextEdit#Editor {
    background: $field; border: 1px solid $border; border-radius: 8px;
    padding: 7px 10px; color: $ink;
    selection-background-color: $focus; selection-color: #FFFFFF;
}
QLineEdit:hover, QDateEdit:hover, QPlainTextEdit#Editor:hover { border-color: $border_strong; }
QLineEdit:focus, QDateEdit:focus, QPlainTextEdit#Editor:focus { border: 1px solid $focus; }
QLineEdit[invalid="true"], QDateEdit[invalid="true"] { border: 1px solid $danger; }
QPlainTextEdit#Editor { font-family: $mono; font-size: 12px; padding: 10px 12px; }
QDateEdit::drop-down {
    subcontrol-origin: padding; subcontrol-position: center right;
    width: 30px; border: none;
}
QDateEdit::down-arrow { image: url("$chevron"); width: 14px; height: 14px; }

/* Botões ------------------------------------------------------------- */
#PrimaryButton {
    background: $accent; color: #FFFFFF; border: none; border-radius: 8px;
    padding: 0 18px; min-height: 40px; font-size: 14px; font-weight: 600;
}
#PrimaryButton:hover { background: $accent_hover; }
#PrimaryButton:pressed { background: $accent_pressed; }
#PrimaryButton:disabled { background: $disabled_bg; color: $ink_faint; }
#PrimaryButton:focus { border: 2px solid $focus; }

#GhostButton {
    background: $surface; color: $ink; border: 1px solid $border;
    border-radius: 8px; padding: 0 14px; min-height: 34px; font-weight: 600;
}
#GhostButton:hover { background: $field; border-color: $border_strong; }
#GhostButton:focus { border-color: $focus; }
#GhostButton:disabled { color: $ink_faint; background: $field; }

#IconButton { background: transparent; border: none; border-radius: 8px; padding: 6px; }
#IconButton:hover { background: $hover; }
#PathBox { background: $field; border: 1px solid $border; border-radius: 8px; min-height: 34px; }
#PathText { color: $ink; font-size: 13px; }
#PathText[empty="true"] { color: $ink_faint; }
#PathBox #IconButton { padding: 5px; border-radius: 6px; }
#FieldButton {
    background: $field; border: 1px solid $border; border-radius: 8px;
    min-width: 36px; max-width: 36px; min-height: 34px;
}
#FieldButton:hover { background: $hover; border-color: $border_strong; }

#Chip {
    background: $field; color: $ink_muted; border: 1px solid $border;
    border-radius: 15px; padding: 0 14px; min-height: 30px; font-weight: 600;
}
#Chip:hover { border-color: $border_strong; color: $ink; }
#Chip:checked { background: $accent_soft; border-color: $accent; color: $accent_text; }

#LinkButton { background: transparent; border: none; color: $accent_text; font-weight: 600; padding: 2px 4px; }
#LinkButton:hover { text-decoration: underline; }

/* Controle segmentado ------------------------------------------------ */
#Segmented { background: $field; border: 1px solid $border; border-radius: 10px; }
#SegButton {
    background: transparent; border: 1px solid transparent; border-radius: 7px;
    padding: 0 14px; min-height: 30px; color: $ink_muted; font-weight: 600;
}
#SegButton:hover { color: $ink; }
#SegButton:checked { background: $surface; color: $ink; border: 1px solid $border; }

/* Etiquetas de status (fundo claro) ---------------------------------- */
#Badge { border-radius: 10px; padding: 3px 10px; font-size: 12px; font-weight: 600; }
#Badge[tone="ok"] { background: $success_soft; color: $success; }
#Badge[tone="warn"] { background: $warn_soft; color: $warn; }
#Badge[tone="error"] { background: $danger_soft; color: $danger; }

/* Console de execução ------------------------------------------------ */
#Console { background: $con_bg; border: 1px solid $con_border; border-radius: 12px; }
#ConsoleTitle { color: #FFFFFF; font-size: 14px; font-weight: 600; }
#ConsoleMeta { color: $con_muted; font-size: 12px; }
#ConsoleText {
    background: transparent; border: none; color: $con_text;
    font-family: $mono; font-size: 12px; selection-background-color: #2F5BEA;
}
#ConsoleButton {
    background: transparent; color: $con_text; border: 1px solid $con_border;
    border-radius: 6px; padding: 0 10px; min-height: 26px; font-size: 12px;
}
#ConsoleButton:hover { background: #111A40; }
QProgressBar#ConsoleProgress { background: #121B40; border: none; border-radius: 2px; }
QProgressBar#ConsoleProgress::chunk { background: $accent; border-radius: 2px; }
#StatusChip { border-radius: 10px; padding: 2px 10px; font-size: 11px; font-weight: 600; }
#StatusChip[state="idle"] { background: #161F48; color: #A3ACCC; }
#StatusChip[state="running"] { background: #3A2410; color: #FFB27A; }
#StatusChip[state="ok"] { background: #0E3326; color: #4BE3A0; }
#StatusChip[state="error"] { background: #3A1418; color: #FF8C8C; }
#StatusChip[state="cancelled"] { background: #33270E; color: #FFC266; }
#ConsoleText QScrollBar:vertical { background: transparent; width: 10px; }
#ConsoleText QScrollBar::handle:vertical { background: #232E5C; border-radius: 4px; min-height: 30px; }

/* Aviso flutuante ---------------------------------------------------- */
#Toast { background: #0A1433; border: 1px solid #24315F; border-radius: 10px; }
#ToastText { color: #FFFFFF; font-size: 13px; }

/* Barras de rolagem -------------------------------------------------- */
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: $border_strong; border-radius: 3px; min-height: 30px; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
QScrollBar::handle:horizontal { background: $border_strong; border-radius: 3px; min-width: 30px; }
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {
    background: none; border: none; width: 0; height: 0;
}

QToolTip { background: #0A1433; color: #FFFFFF; border: none; padding: 6px 8px; border-radius: 6px; }

/* Diálogos ----------------------------------------------------------- */
QMessageBox, QFileDialog { background: $surface; }
QMessageBox QLabel { color: $ink; }
QMessageBox QPushButton {
    background: $surface; color: $ink; border: 1px solid $border; border-radius: 8px;
    min-width: 90px; min-height: 32px; padding: 0 12px; font-weight: 600;
}
QMessageBox QPushButton:hover { background: $field; }
QMessageBox QPushButton:default { background: $accent; color: #FFFFFF; border: none; }

/* Calendário do campo de data ---------------------------------------- */
QCalendarWidget QWidget { alternate-background-color: $field; background: $surface; color: $ink; }
QCalendarWidget QToolButton {
    color: $ink; background: transparent; border: none; border-radius: 6px;
    padding: 4px 8px; font-weight: 600;
}
QCalendarWidget QToolButton:hover { background: $hover; }
QCalendarWidget QAbstractItemView {
    background: $surface; color: $ink; outline: 0;
    selection-background-color: $accent; selection-color: #FFFFFF;
}
QCalendarWidget QAbstractItemView:disabled { color: $ink_faint; }
QCalendarWidget QMenu { background: $surface; color: $ink; }
QCalendarWidget QSpinBox { background: $field; border: 1px solid $border; border-radius: 6px; }
""")


def build_qss(tokens: dict | None = None) -> str:
    t = dict(tokens or current())
    t["mono"] = MONO
    t["sans"] = SANS
    t["chevron"] = _svg_asset("chevron-down", t["ink_muted"])
    return _QSS.substitute(t)
