import sys
from datetime import date
from pathlib import Path

# --------------------------------------------------------------------------
# Onde o programa está
# --------------------------------------------------------------------------
# APP_DIR      -> pasta do projeto (rodando com python) ou pasta onde está o .exe.
#                 É aqui que as pastas de trabalho são criadas.
# RESOURCE_DIR -> de onde vêm os arquivos embutidos (logo etc.). No .exe do
#                 PyInstaller é uma pasta temporária (_MEIPASS) apagada ao fechar,
#                 por isso NUNCA grave nada nela.
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
    RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))
else:
    APP_DIR = RESOURCE_DIR = Path(__file__).resolve().parent

APP_NOME = "Central de RF - Eventos"
APP_VERSAO = "2.3"
LOGO_PATH = RESOURCE_DIR / "assets" / "logo.png"

# --------------------------------------------------------------------------
# Pastas fixas
# --------------------------------------------------------------------------
# As pastas de trabalho ficam na raiz do programa (ao lado do .exe).
# Para agrupá-las numa pasta só, troque por: APP_DIR / "Dados"
PASTA_DADOS = APP_DIR / "setup"

# Subpastas criadas (e conferidas a cada abertura) dentro de PASTA_DADOS.
# chave interna -> (nome da pasta, descrição mostrada na tela)
SUBPASTAS = {
    "cravar_pu":      ("Cravar PU",        "Saída do Cravar PU"),
    "eventos_sac":    ("Eventos SAC",      "Saída dos Eventos SAC"),
    "replicar_fluxo": ("Replicar Fluxo",   "Saída do Replicar fluxo"),
    "listas":         ("Listas de ativos", "Arquivos .txt usados no modo em lote"),
    "config":         ("Config",           "Feeder e configurações da Central"),
}

# Feeder padrão (dentro da subpasta "config"). Pode ser trocado na aba Configurações.
NOME_FEEDER_PADRAO = "Feeder_Local.xlsx"

# Credenciais AWS: sempre o arquivo do AWS CLI do usuário.
# Windows: C:\Users\<usuario>\.aws\credentials. A Central nunca cria esse arquivo.
AWS_CREDENTIALS = Path.home() / ".aws" / "credentials"

# --------------------------------------------------------------------------
# Regras das telas
# --------------------------------------------------------------------------
BASES_PU = ["LZ", "XZ", "OS7", "BN7"]
DATA_MINIMA_EVENTOS = date(2026, 1, 1)

CAMINHO_SITE_AWS = "https://pt.wikipedia.org/wiki/Wikip%C3%A9dia:P%C3%A1gina_principal"
# Depois de quantas horas as credenciais aparecem como "desatualizadas"
AWS_VALIDADE_HORAS = 12
