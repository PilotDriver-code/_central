from core import configuracoes as cfg
from core import processos

from ..qt import QtCore, QtGui, QtWidgets
from ..widgets import Field, PathField, Segmented, hline
from .base import BasePage, mark_invalid

W = QtWidgets


class ReplicarFluxoPage(BasePage):
    title = "Replicar fluxo"
    description = "Replique o fluxo de um ativo pelo código CETIP ou de uma lista inteira."
    nav_icon = "repeat"
    nav_label = "Replicar fluxo"

    def __init__(self, parent=None):
        super().__init__(parent)
        form = self.build_split("Ativos", "Replicar", "repeat")

        self.mode = Segmented(["Ativo único", "Em lote"])
        form.addWidget(self.mode)

        self.stack = W.QStackedWidget()

        # Ativo único
        self.codigo = W.QLineEdit()
        self.codigo.setPlaceholderText("Digite o código CETIP")
        self.codigo.setMaxLength(20)
        rx = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression(r"[A-Za-z0-9]*"), self.codigo)
        self.codigo.setValidator(rx)
        self.codigo.textEdited.connect(self._upper)
        self.codigo.returnPressed.connect(self.run)
        self.f_codigo = Field("Código CETIP", self.codigo)
        self.stack.addWidget(self._wrap(self.f_codigo))

        # Em lote
        self.lista = PathField("file", "Arquivos de texto (*.txt *.csv)", "Um código por linha",
                               start_dir=lambda: cfg.pasta("listas"))
        self.lista.changed.connect(self._preview_lista)
        self.f_lista = Field("Lista de ativos (.txt)", self.lista, "Um código CETIP por linha.")
        self.stack.addWidget(self._wrap(self.f_lista))

        self.stack.setSizePolicy(W.QSizePolicy.Policy.Preferred, W.QSizePolicy.Policy.Maximum)
        form.addWidget(self.stack)
        self.mode.changed.connect(self._switch_mode)

        form.addWidget(hline())

        form.addWidget(self.fixed_path_field("Pasta de saída", lambda: cfg.pasta("replicar_fluxo")))

    @staticmethod
    def _wrap(widget):
        holder = W.QWidget()
        lay = W.QVBoxLayout(holder)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(widget)
        return holder

    def _switch_mode(self, idx: int):
        self.stack.setCurrentIndex(idx)
        (self.codigo if idx == 0 else self.lista.edit).setFocus()

    def _upper(self, text: str):
        pos = self.codigo.cursorPosition()
        self.codigo.setText(text.upper())
        self.codigo.setCursorPosition(pos)
        mark_invalid(self.codigo, False)
        self.f_codigo.set_hint("")

    def _preview_lista(self, path: str):
        if not path:
            self.f_lista.set_hint("Um código CETIP por linha.")
            return
        try:
            ativos = processos.ler_lista_ativos(path)
        except OSError:
            self.f_lista.set_hint("Arquivo não encontrado.", "error")
            return
        if not ativos:
            self.f_lista.set_hint("A lista está vazia.", "error")
        else:
            amostra = ", ".join(ativos[:3]) + ("…" if len(ativos) > 3 else "")
            self.f_lista.set_hint(f"{len(ativos)} ativo(s): {amostra}", "ok")

    def run(self):
        if not self.ensure_ready():
            return
        saida = str(cfg.pasta("replicar_fluxo"))
        if self.mode.index() == 0:
            codigo = self.codigo.text().strip()
            if not codigo:
                mark_invalid(self.codigo, True)
                self.f_codigo.set_hint("Informe o código CETIP do ativo.", "error")
                return
            self.start_task(processos.replicar_fluxo_unico,
                            {"codigo": codigo, "saida": saida}, f"Replicar fluxo: {codigo}")
        else:
            path = self.lista.text()
            try:
                ativos = processos.ler_lista_ativos(path) if path else []
            except OSError:
                ativos = []
            if not ativos:
                self.f_lista.set_hint("Escolha um arquivo .txt com ao menos um código.", "error")
                return
            self.start_task(processos.replicar_fluxo_lote,
                            {"lista": path, "saida": saida}, f"Replicar fluxo em lote: {len(ativos)} ativos")

