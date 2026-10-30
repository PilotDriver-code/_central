from .aws import AWSPage
from .configuracoes import ConfiguracoesPage
from .cravar_pu import CravarPUPage
from .eventos_sac import EventosSACPage
from .replicar_fluxo import ReplicarFluxoPage

# Ordem do menu (e dos atalhos Ctrl+1, Ctrl+2...).
# Telas com `nav_bottom = True` aparecem no rodapé do menu.
PAGES = [CravarPUPage, EventosSACPage, ReplicarFluxoPage, AWSPage, ConfiguracoesPage]
