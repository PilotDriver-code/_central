from datetime import datetime

import config
from core import aws
from core import configuracoes as cfg

from ..qt import QtCore, QtWidgets, Qt
from ..widgets import Badge, GhostButton, Panel, PrimaryButton, hline, label
from .base import BasePage

W = QtWidgets


class AWSPage(BasePage):
    title = "Credenciais AWS"
    description = "Copie as credenciais do portal e cole aqui para atualizar o arquivo do AWS CLI."
    nav_icon = "cloud"
    nav_label = "AWS"

    def __init__(self, parent=None):
        super().__init__(parent)
        root = W.QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        # Situação do arquivo --------------------------------------------
        info = Panel("Arquivo de credenciais")
        info.setFixedWidth(self.FORM_WIDTH)

        info.body.addWidget(label("Última atualização", "FieldLabel"))
        row = W.QHBoxLayout()
        row.setSpacing(10)
        self.lbl_quando = label("", "StatValue")
        row.addWidget(self.lbl_quando)
        row.addStretch(1)
        self.badge = Badge()
        row.addWidget(self.badge, 0, Qt.AlignmentFlag.AlignVCenter)
        info.body.addLayout(row)
        self.lbl_relativo = label("", "Hint", wrap=True)
        info.body.addWidget(self.lbl_relativo)

        info.body.addWidget(hline())
        self.f_path = self.fixed_path_field(
            "Local do arquivo", cfg.arquivo_aws, kind="file",
            hint="Arquivo do AWS CLI deste usuário. O botão ao lado abre a pasta .aws.")
        info.body.addWidget(self.f_path)

        info.body.addStretch(1)
        self.btn_portal = GhostButton("Abrir portal AWS", "external")
        self.btn_portal.clicked.connect(aws.abrir_portal)
        info.body.addWidget(self.btn_portal)

        # Editor ------------------------------------------------------------
        editor_panel = Panel("Colar credenciais")
        self.editor = W.QPlainTextEdit()
        self.editor.setObjectName("Editor")
        self.editor.setPlaceholderText(
            "Cole aqui o bloco de credenciais copiado do portal.\n\n"
            "O conteúdo substitui o arquivo inteiro."
        )
        self.editor.textChanged.connect(self._on_text)
        editor_panel.body.addWidget(self.editor, 1)

        foot = W.QHBoxLayout()
        self.lbl_count = label("", "Hint")
        foot.addWidget(self.lbl_count)
        foot.addStretch(1)
        self.btn_save = PrimaryButton("Atualizar credenciais", "save")
        self.btn_save.setToolTip("Ctrl+Enter")
        self.btn_save.clicked.connect(self.run)
        foot.addWidget(self.btn_save)
        editor_panel.body.addLayout(foot)

        root.addWidget(info)
        root.addWidget(editor_panel, 1)

        # Mantém o "há X min" em dia enquanto a tela estiver aberta.
        self._clock = QtCore.QTimer(self)
        self._clock.setInterval(60_000)
        self._clock.timeout.connect(self.refresh_status)
        self._clock.start()

        self._on_text()
        self.refresh_status()

    def on_shown(self):
        super().on_shown()
        self.refresh_status()
        self.editor.setFocus()  # pronto para colar (Ctrl+V)

    def refresh_status(self):
        quando = aws.ultima_atualizacao()
        self._on_text()
        if quando is None:
            self.lbl_quando.setText("Não encontrado")
            self.lbl_relativo.setText("A Central não cria esse arquivo. Configure o AWS CLI "
                                      "nesta máquina (aws configure) e volte aqui.")
            self.badge.set("Ausente", "error")
            return
        self.lbl_quando.setText(quando.strftime("%d/%m/%Y  %H:%M"))
        self.lbl_relativo.setText(f"Atualizado {aws.tempo_relativo(quando)}")
        horas = (datetime.now() - quando).total_seconds() / 3600
        if horas <= config.AWS_VALIDADE_HORAS:
            self.badge.set("Em dia", "ok")
        else:
            self.badge.set("Desatualizado", "warn")

    def _on_text(self):
        texto = self.editor.toPlainText()
        linhas = len([l for l in texto.splitlines() if l.strip()])
        self.btn_save.setEnabled(bool(texto.strip()) and aws.existe())
        if not aws.existe():
            self.lbl_count.setText("Arquivo de credenciais não encontrado")
        else:
            self.lbl_count.setText(f"{linhas} linha(s)" if linhas else "Nenhum conteúdo colado")

    def run(self):
        texto = self.editor.toPlainText()
        if not texto.strip():
            self.toast("Cole as credenciais antes de atualizar.", "error")
            return
        if not aws.existe():
            self.toast(f"{cfg.arquivo_aws()} não existe. Configure o AWS CLI primeiro.", "error")
            self.refresh_status()
            return
        box = W.QMessageBox(self)
        box.setIcon(W.QMessageBox.Icon.Question)
        box.setWindowTitle("Atualizar credenciais")
        box.setText("Substituir o arquivo de credenciais?")
        box.setInformativeText(f"O conteúdo atual de {cfg.arquivo_aws()} será substituído.")
        ok = box.addButton("Substituir", W.QMessageBox.ButtonRole.AcceptRole)
        box.addButton("Cancelar", W.QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(ok)
        box.exec()
        if box.clickedButton() is not ok:
            return
        try:
            aws.salvar_credenciais(texto)
        except aws.CredenciaisNaoEncontradas as exc:
            self.toast(str(exc), "error")
            self.refresh_status()
            return
        except OSError as exc:
            self.toast(f"Não foi possível gravar o arquivo: {exc}", "error")
            return
        self.editor.clear()
        self.refresh_status()
        self.toast("Credenciais atualizadas.", "ok")
