"""Pastas de trabalho e arquivos da Central, sem dependência de interface.

As pastas ficam na raiz do programa (config.PASTA_DADOS): ao lado do main.py
rodando com Python, ou ao lado do .exe depois de empacotado.

Regras:
  * A cada abertura e antes de cada rotina, as subpastas que faltarem são criadas.
  * O Feeder nunca é criado: se não estiver no lugar, a tela avisa.
  * O arquivo de credenciais AWS é sempre ~/.aws/credentials e nunca é criado aqui.
  * A escolha de um Feeder personalizado fica em Config/configuracoes.json.

Uso no resto do código:
    from core import configuracoes as cfg
    cfg.pasta("cravar_pu")   -> Path da pasta de saída do Cravar PU
    cfg.arquivo_feeder()     -> Path do Feeder
    cfg.arquivo_aws()        -> Path do credentials do AWS CLI
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

import config

_cache: dict | None = None


def arquivo_config() -> Path:
    return pasta("config") / "configuracoes.json"


def _padrao() -> dict:
    return {"arquivo_feeder": ""}


def carregar() -> dict:
    global _cache
    if _cache is None:
        dados = _padrao()
        try:
            dados.update(json.loads(arquivo_config().read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass
        _cache = dados
    return _cache


def salvar(**alteracoes) -> dict:
    """Atualiza e grava. Ex.: salvar(arquivo_feeder="R:/Feeder.xlsx")"""
    dados = carregar()
    dados.update({k: str(v) for k, v in alteracoes.items()})
    garantir_pastas()
    arquivo_config().write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
    return dados


# Pastas ---------------------------------------------------------------------
def pasta_raiz() -> Path:
    return Path(config.PASTA_DADOS)


def pasta(chave: str) -> Path:
    nome, _ = config.SUBPASTAS[chave]
    return pasta_raiz() / nome


def garantir_pastas() -> list[Path]:
    """Cria as subpastas que faltarem e o Feeder modelo. Devolve as pastas criadas agora."""
    criadas = []
    for chave in config.SUBPASTAS:
        p = pasta(chave)
        if not p.is_dir():
            p.mkdir(parents=True, exist_ok=True)
            criadas.append(p)
    garantir_feeder()
    return criadas


# Cabeçalho do Feeder modelo: (texto, cor de fundo, largura da coluna)
FEEDER_COLUNAS = [
    ("ATIVO", "C00000", 14),
    ("JUROS", "153D64", 14),
    ("AMORTIZACAO", "153D64", 22),
    ("VENCIMENTO", "0D3512", 20),
]


def garantir_feeder() -> Path | None:
    """Cria o Feeder_Local.xlsx (só com o cabeçalho) se ele ainda não existir.

    Só mexe no Feeder padrão da pasta Config; um Feeder escolhido em
    Configurações nunca é criado nem alterado. Devolve o caminho se criou.
    """
    if feeder_personalizado():
        return None
    caminho = pasta("config") / config.NOME_FEEDER_PADRAO
    if caminho.exists():
        return None

    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    wb = Workbook()
    ws = wb.active
    ws.title = "Feeder"
    for col, (texto, cor, largura) in enumerate(FEEDER_COLUNAS, start=1):
        cel = ws.cell(row=1, column=col, value=texto)
        cel.font = Font(bold=True, color="FFFFFF", size=12)
        cel.fill = PatternFill("solid", fgColor=cor)
        cel.alignment = Alignment(horizontal="center", vertical="center")
        ws.column_dimensions[cel.column_letter].width = largura
    ws.row_dimensions[1].height = 22
    ws.freeze_panes = "A2"  # cabeçalho fixo ao rolar

    caminho.parent.mkdir(parents=True, exist_ok=True)
    wb.save(caminho)
    return caminho


# Arquivos -------------------------------------------------------------------
def arquivo_feeder() -> Path:
    personalizado = carregar().get("arquivo_feeder")
    if personalizado:
        return Path(personalizado)
    return pasta("config") / config.NOME_FEEDER_PADRAO


def feeder_personalizado() -> bool:
    return bool(carregar().get("arquivo_feeder"))


def arquivo_aws() -> Path:
    return config.AWS_CREDENTIALS


# Verificação ----------------------------------------------------------------
@dataclass
class Situacao:
    pastas_faltando: list[str] = field(default_factory=list)
    feeder_existe: bool = False

    @property
    def primeira_vez(self) -> bool:
        return len(self.pastas_faltando) == len(config.SUBPASTAS)


def verificar() -> Situacao:
    return Situacao(
        pastas_faltando=[k for k in config.SUBPASTAS if not pasta(k).is_dir()],
        feeder_existe=arquivo_feeder().is_file(),
    )
