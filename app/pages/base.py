from core import configuracoes as cfg

from ..qt import QtWidgets, Qt
from ..widgets import Field, LogConsole, Panel, PathDisplay, PrimaryButton, Toast
from ..worker import TaskThread

W = QtWidgets


class BasePage(W.QWidget):
    """Tela padrão: painel de parâmetros à esquerda, console à direita."""

    title = ""
    description = ""
    nav_icon = "info"
    nav_label = ""

    # Proporção entre o painel de comandos (esquerda) e o console (direita).
    FORM_STRETCH = 11
    CONSOLE_STRETCH = 9
    FORM_MIN_WIDTH = 460
    FORM_WIDTH = 400  # usado pela tela AWS (painel informativo)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread: TaskThread | None = None
        self._run_button: PrimaryButton | None = None
        self._fixed_paths: list[tuple[PathDisplay, object]] = []
        self._recriadas = []

    # Montagem -------------------------------------------------------------
    def build_split(self, panel_title: str, action_text: str, action_icon: str = "play"):
        """Cria o layout padrão e devolve o layout do formulário para preencher."""
        root = W.QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        self.form_panel = Panel(panel_title)
        self.form_panel.setMinimumWidth(self.FORM_MIN_WIDTH)
        form = W.QVBoxLayout()
        form.setSpacing(18)
        self.form_panel.body.addLayout(form)
        self.form_panel.body.addStretch(1)

        self._run_button = PrimaryButton(action_text, action_icon)
        self._run_button.setToolTip("Ctrl+Enter")
        self._run_button.clicked.connect(self.run)
        self.form_panel.body.addWidget(self._run_button)

        self.console = LogConsole()
        self.console.cancel_requested.connect(self.cancel)

        self.console.setMinimumWidth(360)
        root.addWidget(self.form_panel, self.FORM_STRETCH)
        root.addWidget(self.console, self.CONSOLE_STRETCH)
        return form

    def fixed_path_field(self, title: str, getter, kind: str = "dir", hint: str | None = None) -> Field:
        """Campo somente leitura com um caminho vindo da aba Configurações.

        `getter` é uma função que devolve o Path atual (ex.: lambda: cfg.pasta("cravar_pu")).
        O caminho é relido toda vez que a tela aparece.
        """
        display = PathDisplay(kind)
        display.set_path(getter())
        self._fixed_paths.append((display, getter))
        return Field(title, display, hint)

    def refresh_paths(self):
        for display, getter in self._fixed_paths:
            display.set_path(getter())

    # Execução -------------------------------------------------------------
    def ensure_ready(self) -> bool:
        """Antes de rodar: cria as subpastas que faltarem (ficam na raiz do programa)."""
        try:
            criadas = cfg.garantir_pastas()
        except OSError as exc:
            self.toast(f"Não foi possível criar as pastas em {cfg.pasta_raiz()}: {exc}", "error")
            return False
        self._recriadas = criadas  # registradas no console quando a rotina começar
        return True

    def run(self):
        """Chamado pelo botão principal / Ctrl+Enter. Subclasses implementam."""

    def is_busy(self) -> bool:
        return self._thread is not None and self._thread.isRunning()

    def start_task(self, fn, params: dict, title: str):
        if self.is_busy():
            return
        self.console.start(title)
        if self._recriadas:
            nomes = ", ".join(p.name for p in self._recriadas)
            self.console.log(f"Subpasta(s) que não existiam foram recriadas: {nomes}", "warn")
            self._recriadas = []
        if self._run_button:
            self._run_button.setEnabled(False)
        self._thread = TaskThread(fn, params, self)
        self._thread.sig_log.connect(self.console.log)
        self._thread.sig_progress.connect(self.console.set_progress)
        self._thread.sig_done.connect(self._on_done)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def cancel(self):
        if self.is_busy():
            self._thread.requestInterruption()
            self.console.btn_cancel.setEnabled(False)
            self.console.log("Cancelando…", "warn")

    def _on_done(self, status: str, message: str):
        ok, cancelled = status == "ok", status == "cancelled"
        self.console.finish(ok, message, cancelled)
        if self._run_button:
            self._run_button.setEnabled(True)
        self._thread = None
        self.toast(message, "ok" if ok else ("warn" if cancelled else "error"))

    # Utilidades -----------------------------------------------------------
    def toast(self, text: str, kind: str = "ok"):
        Toast.show_message(self.window().centralWidget() or self.window(), text, kind)

    def refresh_icons(self):
        for w in self.findChildren(W.QWidget):
            if hasattr(w, "refresh_icons") and w is not self:
                w.refresh_icons()

    def on_shown(self):
        """Chamado sempre que a tela fica visível."""
        self.refresh_paths()


def mark_invalid(widget: W.QWidget, invalid: bool):
    widget.setProperty("invalid", invalid)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    if invalid:
        widget.setFocus(Qt.FocusReason.OtherFocusReason)
