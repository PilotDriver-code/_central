import config
from core import aws
from core import configuracoes as cfg

from .. import icons, theme
from ..qt import QtWidgets, Qt
from ..widgets import (Badge, Field, GhostButton, IconButton, Panel, PathDisplay, Toast, hline,
                       label, open_path)
from .base import BasePage

W = QtWidgets


class FolderRow(W.QWidget):
    """Linha da lista de subpastas: nome, descrição, situação e botão de abrir."""

    def __init__(self, chave: str, parent=None):
        super().__init__(parent)
        self.chave = chave
        nome, descricao = config.SUBPASTAS[chave]
        lay = W.QHBoxLayout(self)
        lay.setContentsMargins(0, 6, 0, 6)
        lay.setSpacing(12)
        self.icon = W.QLabel()
        self.icon.setFixedSize(20, 20)
        lay.addWidget(self.icon)
        col = W.QVBoxLayout()
        col.setSpacing(1)
        t = label(nome)
        t.setStyleSheet("font-weight: 600;")
        col.addWidget(t)
        col.addWidget(label(descricao, "Hint"))
        lay.addLayout(col, 1)
        self.badge = Badge()
        lay.addWidget(self.badge, 0, Qt.AlignmentFlag.AlignVCenter)
        self.btn_open = IconButton("external", "Abrir no Explorer", size=16)
        self.btn_open.clicked.connect(lambda: open_path(cfg.pasta(self.chave)))
        lay.addWidget(self.btn_open)
        self.refresh_icons()

    def refresh_icons(self):
        self.icon.setPixmap(icons.pixmap("folder", theme.current()["ink_muted"], 20))
        self.btn_open.refresh_icons()

    def refresh(self) -> bool:
        p = cfg.pasta(self.chave)
        existe = p.is_dir()
        self.badge.set("Criada" if existe else "Não existe", "ok" if existe else "warn")
        self.btn_open.setEnabled(existe)
        self.setToolTip(str(p))
        return existe


class ConfiguracoesPage(BasePage):
    title = "Configurações"
    description = "Pastas de trabalho e arquivos usados pela Central."
    nav_icon = "settings"
    nav_label = "Configurações"
    nav_bottom = True  # aparece no rodapé do menu

    def __init__(self, parent=None):
        super().__init__(parent)
        root = W.QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        # Pasta do programa + subpastas ---------------------------------------
        pastas = Panel("Pastas de trabalho")
        pastas.body.addWidget(
            label(
                "Ficam na pasta setup, junto do programa. Se alguma for apagada, "
                "ela é recriada ao abrir a Central ou ao rodar uma rotina.",
                "Hint",
                wrap=True,
            )
        )
        self.root_display = PathDisplay("dir")
        pastas.body.addWidget(self.root_display)

        pastas.body.addWidget(hline())
        pastas.body.addWidget(label("Subpastas", "FieldLabel"))
        self.rows = [FolderRow(k) for k in config.SUBPASTAS]
        lista = W.QVBoxLayout()
        lista.setSpacing(0)
        for r in self.rows:
            lista.addWidget(r)
        pastas.body.addLayout(lista)
        pastas.body.addStretch(1)

        self.btn_create = GhostButton("Criar pastas que faltam", "rotate")
        self.btn_create.clicked.connect(self._create)
        pastas.body.addWidget(self.btn_create)

        # Arquivos -------------------------------------------------------------
        arquivos = Panel("Arquivos")

        # Feeder: padrão dentro de Config, ou outro arquivo escolhido
        self.feeder_display = PathDisplay("file")
        self.f_feeder = Field("Feeder", self.feeder_display)
        arquivos.body.addWidget(self.f_feeder)
        frow = W.QHBoxLayout()
        frow.setSpacing(8)
        self.btn_feeder = GhostButton("Usar outro arquivo…")
        self.btn_feeder.clicked.connect(self._choose_feeder)
        frow.addWidget(self.btn_feeder)
        self.btn_feeder_reset = W.QPushButton("Voltar ao padrão")
        self.btn_feeder_reset.setObjectName("LinkButton")
        self.btn_feeder_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_feeder_reset.clicked.connect(self._reset_feeder)
        frow.addWidget(self.btn_feeder_reset)
        frow.addStretch(1)
        arquivos.body.addLayout(frow)

        arquivos.body.addWidget(hline())

        # AWS: fixo, só leitura
        self.aws_display = PathDisplay("file")
        self.f_aws = Field("Credenciais AWS", self.aws_display)
        arquivos.body.addWidget(self.f_aws)
        arow = W.QHBoxLayout()
        arow.addStretch(1)
        self.aws_badge = Badge()
        arow.insertWidget(0, self.aws_badge)
        arquivos.body.addLayout(arow)

        arquivos.body.addStretch(1)
        arquivos.body.addWidget(hline())
        arquivos.body.addWidget(label("A escolha do Feeder fica salva em Config\\configuracoes.json, "
                                      "junto do programa.", "Hint", wrap=True))

        root.addWidget(pastas, 1)
        root.addWidget(arquivos, 1)

    # ------------------------------------------------------------------------
    def on_shown(self):
        super().on_shown()
        self.refresh()

    def refresh(self):
        self.root_display.set_path(cfg.pasta_raiz())
        faltando = [r for r in self.rows if not r.refresh()]
        self.btn_create.setVisible(bool(faltando))

        # Feeder
        feeder = cfg.arquivo_feeder()
        self.feeder_display.set_path(feeder)
        self.btn_feeder_reset.setVisible(cfg.feeder_personalizado())
        origem = "Arquivo personalizado" if cfg.feeder_personalizado() else \
            f"Padrão: {config.NOME_FEEDER_PADRAO} dentro da pasta Config"
        if feeder.is_file():
            self.f_feeder.set_hint(origem)
        else:
            self.f_feeder.set_hint(f"{origem}. Arquivo não encontrado: copie o Feeder para esse local.", "error")

        # AWS
        self.aws_display.set_path(cfg.arquivo_aws())
        if aws.existe():
            self.aws_badge.set("Encontrado", "ok")
            self.f_aws.set_hint("Arquivo do AWS CLI deste usuário. É atualizado pela aba AWS.")
        else:
            self.aws_badge.set("Não encontrado", "error")
            self.f_aws.set_hint("A Central não cria esse arquivo. Configure o AWS CLI nesta máquina "
                                "(aws configure).", "error")

    # Ações -------------------------------------------------------------------
    def _create(self):
        try:
            criadas = cfg.garantir_pastas()
        except OSError as exc:
            self.toast(f"Não foi possível criar as pastas: {exc}", "error")
            return
        self.refresh()
        self.toast(f"{len(criadas)} pasta(s) criada(s)." if criadas else "Todas as pastas já existem.", "ok")

    def _choose_feeder(self):
        start = str(cfg.arquivo_feeder().parent)
        path, _ = W.QFileDialog.getOpenFileName(self, "Escolher Feeder", start,
                                                "Planilhas Excel (*.xlsx *.xlsm *.xls)")
        if path:
            try:
                cfg.salvar(arquivo_feeder=path)
            except OSError as exc:
                self.toast(f"Não foi possível salvar a configuração: {exc}", "error")
                return
            self.refresh()
            Toast.show_message(self.window().centralWidget(), "Feeder atualizado.", "ok")

    def _reset_feeder(self):
        try:
            cfg.salvar(arquivo_feeder="")
        except OSError as exc:
            self.toast(f"Não foi possível salvar a configuração: {exc}", "error")
            return
        self.refresh()
