"""Execução de rotinas em segundo plano, sem travar a janela."""

import traceback

from .qt import QtCore, Signal


class Cancelled(Exception):
    """Levante (ou deixe ctx.check() levantar) para interromper a rotina."""


class TaskContext:
    """Objeto entregue às rotinas do `core` para conversar com a interface.

    Uso dentro de uma rotina:
        ctx.log("Lendo Feeder...", "step")
        ctx.progress(40)
        ctx.check()   # interrompe se o usuário clicou em Cancelar
    """

    def __init__(self, thread: "TaskThread"):
        self._thread = thread

    def log(self, message: str, level: str = "info") -> None:
        self._thread.sig_log.emit(str(message), level)

    def progress(self, pct: float) -> None:
        self._thread.sig_progress.emit(int(pct))

    @property
    def cancelled(self) -> bool:
        return self._thread.isInterruptionRequested()

    def check(self) -> None:
        if self.cancelled:
            raise Cancelled()


class TaskThread(QtCore.QThread):
    sig_log = Signal(str, str)
    sig_progress = Signal(int)
    sig_done = Signal(str, str)  # status (ok | error | cancelled), mensagem

    def __init__(self, fn, params: dict, parent=None):
        super().__init__(parent)
        self._fn = fn
        self._params = params

    def run(self):
        ctx = TaskContext(self)
        try:
            result = self._fn(self._params, ctx)
            self.sig_done.emit("ok", result or "Rotina concluída.")
        except Cancelled:
            self.sig_done.emit("cancelled", "Rotina cancelada pelo usuário.")
        except Exception as exc:  # noqa: BLE001 - qualquer erro vai para o console
            self.sig_log.emit(traceback.format_exc().rstrip(), "error")
            self.sig_done.emit("error", f"Falhou: {exc}")
