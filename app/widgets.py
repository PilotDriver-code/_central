"""Componentes reutilizáveis da interface."""

import html
from datetime import datetime
from pathlib import Path

from . import icons, theme
from .qt import Property, QtCore, QtGui, QtWidgets, Qt, Signal

W = QtWidgets
Policy = W.QSizePolicy.Policy


def repolish(widget: W.QWidget) -> None:
    """Reaplica o QSS depois de trocar uma propriedade dinâmica."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def label(text: str, obj: str | None = None, wrap: bool = False) -> W.QLabel:
    lbl = W.QLabel(text)
    if obj:
        lbl.setObjectName(obj)
    lbl.setWordWrap(wrap)
    return lbl


def hline() -> W.QFrame:
    line = W.QFrame()
    line.setObjectName("Divider")
    return line


class PrimaryButton(W.QPushButton):
    def __init__(self, text: str, icon_name: str | None = None, parent=None):
        super().__init__(text, parent)
        self.setObjectName("PrimaryButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)  # contorno só ao navegar com Tab
        self._icon_name = icon_name
        self.refresh_icons()

    def refresh_icons(self):
        if self._icon_name:
            self.setIcon(icons.icon(self._icon_name, "#FFFFFF", size=16,
                                    disabled=theme.current()["ink_faint"]))
            self.setIconSize(QtCore.QSize(16, 16))


class GhostButton(W.QPushButton):
    def __init__(self, text: str, icon_name: str | None = None, parent=None):
        super().__init__(text, parent)
        self.setObjectName("GhostButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self._icon_name = icon_name
        self.refresh_icons()

    def refresh_icons(self):
        if self._icon_name:
            self.setIcon(icons.icon(self._icon_name, theme.current()["ink"], size=16))
            self.setIconSize(QtCore.QSize(16, 16))


class IconButton(W.QToolButton):
    def __init__(self, icon_name: str, tooltip: str, obj: str = "IconButton",
                 size: int = 18, color_key: str = "ink_muted", parent=None):
        super().__init__(parent)
        self.setObjectName(obj)
        self.setToolTip(tooltip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._icon_name, self._size, self._color_key = icon_name, size, color_key
        self.refresh_icons()

    def set_icon_name(self, name: str):
        self._icon_name = name
        self.refresh_icons()

    def refresh_icons(self):
        color = theme.current().get(self._color_key, self._color_key)
        self.setIcon(icons.icon(self._icon_name, color, size=self._size))
        self.setIconSize(QtCore.QSize(self._size, self._size))


# --------------------------------------------------------------------------
# Menu lateral
# --------------------------------------------------------------------------
class NavButton(W.QPushButton):
    """Item do menu lateral. Mostra só o ícone quando o menu está recolhido."""

    def __init__(self, text: str, icon_name: str, checkable: bool = True, parent=None):
        super().__init__(text, parent)
        self.setObjectName("NavButton")
        self.setCheckable(checkable)
        self.setAutoExclusive(checkable)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)
        self._label = text
        self._icon_name = icon_name
        self.setToolTip("")
        self.refresh_icons()

    def refresh_icons(self):
        t = theme.current()
        self.setIcon(icons.icon(self._icon_name, t["sidebar_text"], "#FFFFFF", size=20))
        self.setIconSize(QtCore.QSize(20, 20))

    def set_collapsed(self, collapsed: bool):
        self.setText("" if collapsed else f"  {self._label}")
        self.setToolTip(self._label if collapsed else "")

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.isChecked():
            p = QtGui.QPainter(self)
            p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QtGui.QColor(theme.current()["accent"]))
            p.drawRoundedRect(QtCore.QRectF(0, 10, 3, self.height() - 20), 1.5, 1.5)
            p.end()


# --------------------------------------------------------------------------
# Campos
# --------------------------------------------------------------------------
class Switch(W.QAbstractButton):
    """Interruptor liga/desliga com animação."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._pos = 0.0
        self._anim = QtCore.QPropertyAnimation(self, b"knob", self)
        self._anim.setDuration(140)
        self._anim.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
        self.toggled.connect(self._animate)

    def sizeHint(self):
        return QtCore.QSize(40, 22)

    def _get_knob(self):
        return self._pos

    def _set_knob(self, value):
        self._pos = value
        self.update()

    knob = Property(float, _get_knob, _set_knob)

    def _animate(self, checked: bool):
        self._anim.stop()
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    def setChecked(self, checked: bool):  # noqa: N802 - API Qt
        super().setChecked(checked)
        if self._anim.state() != QtCore.QAbstractAnimation.State.Running:
            self._pos = 1.0 if checked else 0.0
            self.update()

    def paintEvent(self, _):
        t = theme.current()
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        r = QtCore.QRectF(1, 1, 38, 20)
        off, on = QtGui.QColor(t["border_strong"]), QtGui.QColor(t["accent"])
        track = QtGui.QColor(
            int(off.red() + (on.red() - off.red()) * self._pos),
            int(off.green() + (on.green() - off.green()) * self._pos),
            int(off.blue() + (on.blue() - off.blue()) * self._pos),
        )
        if self.hasFocus():
            p.setPen(QtGui.QPen(QtGui.QColor(t["focus"]), 1.5))
        else:
            p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(track)
        p.drawRoundedRect(r, 10, 10)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QtGui.QColor("#FFFFFF"))
        x = 3 + self._pos * 18
        p.drawEllipse(QtCore.QRectF(x, 3, 16, 16))
        p.end()


class SwitchRow(W.QWidget):
    """Linha com rótulo (e descrição opcional) à esquerda e interruptor à direita."""

    def __init__(self, title: str, description: str | None = None, parent=None):
        super().__init__(parent)
        lay = W.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        col = W.QVBoxLayout()
        col.setSpacing(2)
        t = label(title)
        t.setStyleSheet("font-weight: 600;")
        col.addWidget(t)
        if description:
            col.addWidget(label(description, "Hint", wrap=True))
        lay.addLayout(col, 1)
        self.switch = Switch()
        lay.addWidget(self.switch, 0, Qt.AlignmentFlag.AlignVCenter)
        t.setBuddy(self.switch)

    def mousePressEvent(self, e):
        self.switch.toggle()
        super().mousePressEvent(e)

    def isChecked(self):  # noqa: N802
        return self.switch.isChecked()

    def setChecked(self, v):  # noqa: N802
        self.switch.setChecked(v)


class Field(W.QWidget):
    """Rótulo + controle + dica opcional, empilhados."""

    def __init__(self, title: str, control: W.QWidget, hint: str | None = None, parent=None):
        super().__init__(parent)
        lay = W.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self.title = label(title, "FieldLabel")
        lay.addWidget(self.title)
        lay.addWidget(control)
        self.hint = label(hint or "", "Hint", wrap=True)
        self.hint.setVisible(bool(hint))
        lay.addWidget(self.hint)
        self.control = control

    def set_hint(self, text: str, tone: str = ""):
        self.hint.setText(text)
        self.hint.setVisible(bool(text))
        self.hint.setProperty("tone", tone)
        repolish(self.hint)


class PathField(W.QWidget):
    """Caminho editável + botão para escolher arquivo ou pasta."""

    changed = Signal(str)

    def __init__(self, mode: str = "dir", file_filter: str = "Todos os arquivos (*)",
                 placeholder: str = "", start_dir=None, parent=None):
        super().__init__(parent)
        self._mode, self._filter = mode, file_filter
        self._start_dir = start_dir  # função que devolve a pasta inicial do diálogo
        lay = W.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self.edit = W.QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        self.edit.textChanged.connect(self.changed)
        self.edit.textChanged.connect(self.edit.setToolTip)
        lay.addWidget(self.edit, 1)
        tip = "Escolher pasta" if mode == "dir" else "Escolher arquivo"
        self.button = IconButton("folder" if mode == "dir" else "file", tip, obj="FieldButton", size=16)
        self.button.clicked.connect(self._browse)
        lay.addWidget(self.button)

    def refresh_icons(self):
        self.button.refresh_icons()

    def _browse(self):
        inicial = self._start_dir() if self._start_dir else None
        start = self.edit.text() or (str(inicial) if inicial else "")
        if self._mode == "dir":
            path = W.QFileDialog.getExistingDirectory(self, "Escolher pasta", start)
        else:
            path, _ = W.QFileDialog.getOpenFileName(self, "Escolher arquivo", start, self._filter)
        if path:
            self.edit.setText(path)

    def text(self) -> str:
        return self.edit.text().strip()

    def setText(self, value: str):  # noqa: N802
        self.edit.setText(str(value))


class ChipGroup(W.QWidget):
    """Seleção múltipla em pílulas, com atalho para marcar todas."""

    changed = Signal(list)

    def __init__(self, options: list[str], all_label: str | None = "Todas", parent=None):
        super().__init__(parent)
        lay = W.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        self._chips: list[W.QPushButton] = []
        for opt in options:
            chip = self._make_chip(opt)
            chip.toggled.connect(self._on_toggle)
            self._chips.append(chip)
            lay.addWidget(chip)
        self._all = None
        if all_label:
            self._all = self._make_chip(all_label)
            self._all.clicked.connect(self._on_all)
            lay.addWidget(self._all)
        lay.addStretch(1)

    def _make_chip(self, text):
        chip = W.QPushButton(text)
        chip.setObjectName("Chip")
        chip.setCheckable(True)
        chip.setCursor(Qt.CursorShape.PointingHandCursor)
        return chip

    def _on_all(self, checked: bool):
        for c in self._chips:
            c.blockSignals(True)
            c.setChecked(checked)
            c.blockSignals(False)
        self.changed.emit(self.selected())

    def _on_toggle(self, _):
        if self._all:
            self._all.setChecked(all(c.isChecked() for c in self._chips))
        self.changed.emit(self.selected())

    def selected(self) -> list[str]:
        return [c.text() for c in self._chips if c.isChecked()]

    def clear(self):
        for c in self._chips + ([self._all] if self._all else []):
            c.setChecked(False)


class Segmented(W.QFrame):
    """Controle segmentado (abas compactas)."""

    changed = Signal(int)

    def __init__(self, options: list[str], parent=None):
        super().__init__(parent)
        self.setObjectName("Segmented")
        lay = W.QHBoxLayout(self)
        lay.setContentsMargins(3, 3, 3, 3)
        lay.setSpacing(2)
        self._group = W.QButtonGroup(self)
        self._group.setExclusive(True)
        for i, opt in enumerate(options):
            b = W.QPushButton(opt)
            b.setObjectName("SegButton")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            self._group.addButton(b, i)
            lay.addWidget(b, 1)
        self._group.button(0).setChecked(True)
        self._group.idClicked.connect(self.changed)

    def index(self) -> int:
        return self._group.checkedId()


class Panel(W.QFrame):
    """Superfície branca com título opcional."""

    def __init__(self, title: str | None = None, parent=None, margins: int = 20, spacing: int = 16):
        super().__init__(parent)
        self.setObjectName("Panel")
        self.body = W.QVBoxLayout(self)
        self.body.setContentsMargins(margins, margins, margins, margins)
        self.body.setSpacing(spacing)
        if title:
            self.body.addWidget(label(title, "PanelTitle"))


class Badge(W.QLabel):
    def __init__(self, text: str = "", tone: str = "ok", parent=None):
        super().__init__(text, parent)
        self.setObjectName("Badge")
        self.set(text, tone)

    def set(self, text: str, tone: str):
        self.setText(text)
        self.setProperty("tone", tone)
        repolish(self)


def open_path(path) -> bool:
    """Abre a pasta no Explorer. Se for arquivo, abre a pasta onde ele está."""
    if not path:
        return False
    p = Path(path)
    alvo = p if p.is_dir() else p.parent
    if not alvo.exists():
        return False
    return QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(alvo)))


class ElidedLabel(W.QLabel):
    """Rótulo que corta o texto no meio (C:\\Users\\...\\Cravar PU) se não couber."""

    def __init__(self, text: str = "", obj: str | None = None, parent=None):
        super().__init__(parent)
        if obj:
            self.setObjectName(obj)
        self._full = text
        self.setSizePolicy(Policy.Ignored, Policy.Preferred)
        self.setText(text)

    def setText(self, text: str):  # noqa: N802
        self._full = str(text)
        self.setToolTip(self._full)
        self._elide()

    def full_text(self) -> str:
        return self._full

    def resizeEvent(self, e):  # noqa: N802
        super().resizeEvent(e)
        self._elide()

    def _elide(self):
        fm = self.fontMetrics()
        super().setText(fm.elidedText(self._full, Qt.TextElideMode.ElideMiddle, max(self.width(), 40)))


class PathDisplay(W.QFrame):
    """Caminho fixo (somente leitura) com botão para abrir no Explorer."""

    def __init__(self, kind: str = "dir", parent=None):
        super().__init__(parent)
        self.setObjectName("PathBox")
        self._kind = kind
        self._path: Path | None = None
        lay = W.QHBoxLayout(self)
        lay.setContentsMargins(10, 4, 4, 4)
        lay.setSpacing(8)
        self.icon = W.QLabel()
        self.icon.setFixedSize(16, 16)
        lay.addWidget(self.icon)
        self.text = ElidedLabel("", "PathText")
        lay.addWidget(self.text, 1)
        self.button = IconButton("external", "Abrir no Explorer", size=15)
        self.button.clicked.connect(lambda: open_path(self._path))
        lay.addWidget(self.button)
        self.refresh_icons()

    def refresh_icons(self):
        self.icon.setPixmap(icons.pixmap("folder" if self._kind == "dir" else "file",
                                         theme.current()["ink_faint"], 16))
        self.button.refresh_icons()

    def set_path(self, path, empty_text: str = "Não definido. Escolha a pasta em Configurações."):
        """Mostra o caminho. Com `path=None`, mostra `empty_text` e desativa o botão."""
        self._path = Path(path) if path else None
        self.text.setText(str(self._path) if self._path else empty_text)
        self.text.setProperty("empty", self._path is None)
        repolish(self.text)
        self.button.setEnabled(self._path is not None)

    def path(self) -> Path | None:
        return self._path

    def exists(self) -> bool:
        return bool(self._path and self._path.exists())


# --------------------------------------------------------------------------
# Console de execução
# --------------------------------------------------------------------------
class LogConsole(W.QFrame):
    """Painel escuro que mostra o andamento de uma rotina."""

    cancel_requested = Signal()

    _STATES = {
        "idle": "Pronto",
        "running": "Executando",
        "ok": "Concluído",
        "error": "Falhou",
        "cancelled": "Cancelado",
    }

    def __init__(self, title: str = "Execução", parent=None):
        super().__init__(parent)
        self.setObjectName("Console")
        self._started: datetime | None = None
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        lay = W.QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 14)
        lay.setSpacing(10)

        head = W.QHBoxLayout()
        head.setSpacing(10)
        head.addWidget(label(title, "ConsoleTitle"))
        self.status = W.QLabel()
        self.status.setObjectName("StatusChip")
        head.addWidget(self.status)
        self.meta = label("", "ConsoleMeta")
        head.addWidget(self.meta)
        head.addStretch(1)

        self.btn_cancel = self._console_button("Cancelar", "stop")
        self.btn_cancel.clicked.connect(self.cancel_requested)
        self.btn_cancel.hide()
        self.btn_copy = self._console_button("Copiar", "copy")
        self.btn_copy.clicked.connect(self._copy)
        self.btn_clear = self._console_button("Limpar", "trash")
        self.btn_clear.clicked.connect(self.clear)
        for b in (self.btn_cancel, self.btn_copy, self.btn_clear):
            head.addWidget(b)
        lay.addLayout(head)

        self.progress = W.QProgressBar()
        self.progress.setObjectName("ConsoleProgress")
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        lay.addWidget(self.progress)

        self.text = W.QPlainTextEdit()
        self.text.setObjectName("ConsoleText")
        self.text.setReadOnly(True)
        self.text.setMaximumBlockCount(5000)
        self.text.setPlaceholderText("O andamento da rotina aparece aqui assim que você iniciar.")
        self.text.setFrameShape(W.QFrame.Shape.NoFrame)
        lay.addWidget(self.text, 1)

        self._set_state("idle")

    def _console_button(self, text, icon_name):
        b = W.QPushButton(text)
        b.setObjectName("ConsoleButton")
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setIcon(icons.icon(icon_name, theme.current()["con_text"], size=14))
        b.setIconSize(QtCore.QSize(14, 14))
        return b

    def _set_state(self, state: str):
        self.status.setText(self._STATES[state])
        self.status.setProperty("state", state)
        repolish(self.status)

    def _tick(self):
        if self._started:
            secs = int((datetime.now() - self._started).total_seconds())
            self.meta.setText(f"{secs // 60:02d}:{secs % 60:02d}")

    # API pública -----------------------------------------------------------
    def start(self, title: str):
        self._started = datetime.now()
        self.progress.setValue(0)
        self._set_state("running")
        self.btn_cancel.show()
        self.btn_cancel.setEnabled(True)
        self.btn_clear.setEnabled(False)
        if self.text.document().characterCount() > 1:
            self.text.appendPlainText("")
        self.log(title, "title")
        self._tick()
        self._timer.start()

    def log(self, message: str, level: str = "info"):
        t = theme.current()
        stamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "info": t["con_text"], "ok": t["con_ok"], "warn": t["con_warn"],
            "error": t["con_error"], "title": "#FFFFFF", "step": t["con_info"],
        }
        marks = {"ok": "✓", "warn": "!", "error": "✕", "step": "›", "title": "▸", "info": " "}
        color = colors.get(level, t["con_text"])
        weight = "font-weight:600;" if level == "title" else ""
        lines = html.escape(str(message)).splitlines() or [""]
        body = "<br>".join(lines)
        self.text.appendHtml(
            f'<span style="color:{t["con_muted"]}">{stamp}</span>&nbsp;&nbsp;'
            f'<span style="color:{color}">{marks.get(level, " ")}</span>&nbsp;'
            f'<span style="color:{color};{weight}">{body}</span>'
        )
        sb = self.text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def set_progress(self, pct: int):
        self.progress.setValue(max(0, min(100, pct)))

    def finish(self, ok: bool, message: str, cancelled: bool = False):
        self._timer.stop()
        self._tick()
        self.progress.setValue(100 if ok else self.progress.value())
        state = "cancelled" if cancelled else ("ok" if ok else "error")
        self._set_state(state)
        self.btn_cancel.hide()
        self.btn_clear.setEnabled(True)
        self.log(message, {"ok": "ok", "error": "error", "cancelled": "warn"}[state])

    def clear(self):
        self.text.clear()
        self.progress.setValue(0)
        self.meta.setText("")
        self._set_state("idle")

    def _copy(self):
        QtGui.QGuiApplication.clipboard().setText(self.text.toPlainText())
        Toast.show_message(self.window(), "Registro copiado para a área de transferência.", "ok")


# --------------------------------------------------------------------------
# Aviso flutuante
# --------------------------------------------------------------------------
class Toast(W.QFrame):
    """Aviso curto no canto inferior direito, some sozinho."""

    _current = None

    def __init__(self, parent: W.QWidget, text: str, kind: str = "ok"):
        super().__init__(parent)
        self.setObjectName("Toast")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        t = theme.current()
        icon_name, color = {
            "ok": ("check", t["con_ok"]),
            "error": ("alert", t["con_error"]),
            "warn": ("alert", t["con_warn"]),
            "info": ("info", t["con_info"]),
        }.get(kind, ("info", t["con_info"]))
        lay = W.QHBoxLayout(self)
        lay.setContentsMargins(14, 11, 16, 11)
        lay.setSpacing(10)
        ic = W.QLabel()
        ic.setPixmap(icons.pixmap(icon_name, color, 18, 2.2))
        lay.addWidget(ic)
        msg = label(text, "ToastText")
        if len(text) > 56:  # só quebra linha em mensagens longas
            msg.setWordWrap(True)
            msg.setFixedWidth(380)
        lay.addWidget(msg)

        self._fx = W.QGraphicsOpacityEffect(self)
        self._fx.setOpacity(0.0)
        self.setGraphicsEffect(self._fx)
        self._anim = QtCore.QPropertyAnimation(self._fx, b"opacity", self)
        self._anim.setDuration(160)

    def _place(self):
        self.adjustSize()
        p = self.parentWidget()
        # canto superior direito, ao lado do botão de tema (não cobre botões de ação)
        self.move(p.width() - self.width() - 84, 22)

    def popup(self, msecs: int = 3200):
        self._place()
        self.show()
        self.raise_()
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()
        # Timer filho do toast: se o toast for destruído antes, o timer vai junto.
        self._timer = QtCore.QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._fade_out)
        self._timer.start(msecs)

    def _fade_out(self):
        self._anim.stop()
        self._anim.setStartValue(self._fx.opacity())
        self._anim.setEndValue(0.0)
        self._anim.finished.connect(self.deleteLater)
        self._anim.start()

    @classmethod
    def show_message(cls, parent: W.QWidget, text: str, kind: str = "ok"):
        try:
            if cls._current is not None:
                cls._current.deleteLater()
        except RuntimeError:
            pass
        toast = cls(parent, text, kind)
        cls._current = toast
        toast.popup()
        return toast
