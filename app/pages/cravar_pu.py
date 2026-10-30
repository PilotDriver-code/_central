import config
from core import configuracoes as cfg
from core import processos

from ..widgets import ChipGroup, Field, SwitchRow, hline
from .base import BasePage


class CravarPUPage(BasePage):
    title = "Cravar PU"
    description = "Escolha as bases para gerar os arquivos de PU a partir do Feeder."
    nav_icon = "banknote"
    nav_label = "Cravar PU"

    def __init__(self, parent=None):
        super().__init__(parent)
        form = self.build_split("Parâmetros", "Processar")

        self.bases = ChipGroup(config.BASES_PU)
        self.f_bases = Field("Bases", self.bases)
        self.bases.changed.connect(lambda sel: self.f_bases.set_hint(""))
        form.addWidget(self.f_bases)

        self.f_feeder = self.fixed_path_field("Feeder", cfg.arquivo_feeder, kind="file")
        form.addWidget(self.f_feeder)
        form.addWidget(self.fixed_path_field("Pasta de saída", lambda: cfg.pasta("cravar_pu")))

        form.addWidget(hline())

        self.sw_feeder = SwitchRow("Feeder atualizado", "Marque se o Feeder local já está na versão do dia.")
        form.addWidget(self.sw_feeder)
        self.sw_carteiras = SwitchRow("Exportar carteiras")
        form.addWidget(self.sw_carteiras)

    def on_shown(self):
        super().on_shown()
        self._check_feeder()

    def _check_feeder(self) -> bool:
        feeder = cfg.arquivo_feeder()
        if feeder is None:
            self.f_feeder.set_hint("")
            return False
        if feeder.is_file():
            self.f_feeder.set_hint("")
            return True
        self.f_feeder.set_hint("Arquivo não encontrado. Coloque o Feeder nessa pasta "
                               "ou indique outro em Configurações.", "error")
        return False

    def run(self):
        if not self.ensure_ready():
            return
        bases = self.bases.selected()
        if not bases:
            self.f_bases.set_hint("Selecione ao menos uma base.", "error")
            self.toast("Selecione ao menos uma base para processar.", "error")
            return
        if not self._check_feeder():
            self.toast("Feeder não encontrado. Confira o caminho em Configurações.", "error")
            return
        params = {
            "bases": bases,
            "feeder": str(cfg.arquivo_feeder()),
            "saida": str(cfg.pasta("cravar_pu")),
            "feeder_atualizado": self.sw_feeder.isChecked(),
            "exportar_carteiras": self.sw_carteiras.isChecked(),
        }
        self.start_task(processos.cravar_pu, params, "Cravar PU")
