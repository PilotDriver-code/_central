"""Credenciais AWS (sem dependência de interface).

O arquivo é sempre o do AWS CLI: C:\\Users\\<usuario>\\.aws\\credentials.
A Central só substitui o conteúdo; se o arquivo não existir, nada é criado.
"""

import webbrowser
from datetime import datetime

import config
from core import configuracoes as cfg


class CredenciaisNaoEncontradas(FileNotFoundError):
    pass


def abrir_portal() -> None:
    webbrowser.open(config.CAMINHO_SITE_AWS)


def existe() -> bool:
    return cfg.arquivo_aws().is_file()


def ultima_atualizacao() -> datetime | None:
    """Data de modificação do arquivo, ou None se ele não existir."""
    caminho = cfg.arquivo_aws()
    if not caminho.is_file():
        return None
    return datetime.fromtimestamp(caminho.stat().st_mtime)


def salvar_credenciais(texto: str) -> datetime:
    caminho = cfg.arquivo_aws()
    if not caminho.is_file():
        raise CredenciaisNaoEncontradas(
            f"{caminho} não existe. Configure o AWS CLI nesta máquina antes de atualizar."
        )
    # "r+" só abre arquivo que já existe: garante que nada novo é criado.
    with open(caminho, "r+", encoding="utf-8", newline="\n") as fh:
        fh.seek(0)
        fh.write(texto.strip() + "\n")
        fh.truncate()
    return ultima_atualizacao()


def tempo_relativo(quando: datetime | None) -> str:
    if quando is None:
        return "nunca"
    seg = int((datetime.now() - quando).total_seconds())
    if seg < 60:
        return "agora há pouco"
    if seg < 3600:
        return f"há {seg // 60} min"
    if seg < 86400:
        return f"há {seg // 3600} h"
    dias = seg // 86400
    return f"há {dias} dia" + ("s" if dias > 1 else "")
