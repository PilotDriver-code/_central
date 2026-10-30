"""Rotinas de processamento chamadas pelas telas.

Cada função recebe:
    params -> dict com o que o usuário preencheu na tela
    ctx    -> TaskContext, para mandar mensagens/progresso para o console

E roda numa thread separada: pode demorar à vontade que a janela não trava.
NÃO mexa em widgets daqui; use só ctx.log / ctx.progress / ctx.check.

>>> As funções abaixo apenas SIMULAM as etapas. Troque o corpo de cada uma
>>> pela lógica real (pandas, leitura do Feeder, chamadas à AWS etc.).
"""

import time
from pathlib import Path


def _simular(ctx, etapas, pausa=0.6):
    total = len(etapas)
    for i, etapa in enumerate(etapas, start=1):
        ctx.check()
        ctx.log(etapa, "step")
        time.sleep(pausa)
        ctx.progress(i / total * 100)


def cravar_pu(params: dict, ctx) -> str:
    bases = params["bases"]
    ctx.log(f"Bases: {', '.join(bases)}")
    ctx.log(f"Feeder: {params['feeder']}")
    if not params["feeder_atualizado"]:
        ctx.log("Feeder não marcado como atualizado — confira antes de enviar.", "warn")

    etapas = ["Lendo Feeder"]
    etapas += [f"Cravando PU da base {b}" for b in bases]
    if params["exportar_carteiras"]:
        etapas.append("Exportando carteiras")
    etapas.append(f"Gravando arquivos em {params['saida']}")
    _simular(ctx, etapas)
    return f"PU cravado para {len(bases)} base(s)."


def eventos_sac(params: dict, ctx) -> str:
    ini, fim = params["inicio"], params["fim"]
    ctx.log(f"Período: {ini:%d/%m/%Y} a {fim:%d/%m/%Y}")
    _simular(ctx, [
        "Conectando ao SAC",
        "Consultando eventos do período",
        "Consolidando resultados",
        f"Gravando planilha em {params['saida']}",
    ])
    return "Eventos SAC exportados."


def replicar_fluxo_unico(params: dict, ctx) -> str:
    codigo = params["codigo"]
    _simular(ctx, [
        f"Buscando fluxo do ativo {codigo}",
        "Replicando eventos",
        f"Gravando arquivo em {params['saida']}",
    ])
    return f"Fluxo do ativo {codigo} replicado."


def ler_lista_ativos(caminho: str) -> list[str]:
    """Um código por linha; ignora linhas vazias e duplicadas."""
    linhas = Path(caminho).read_text(encoding="utf-8", errors="ignore").splitlines()
    vistos, ativos = set(), []
    for linha in linhas:
        cod = linha.strip().upper()
        if cod and cod not in vistos:
            vistos.add(cod)
            ativos.append(cod)
    return ativos


def replicar_fluxo_lote(params: dict, ctx) -> str:
    ativos = ler_lista_ativos(params["lista"])
    ctx.log(f"{len(ativos)} ativo(s) na lista")
    for i, cod in enumerate(ativos, start=1):
        ctx.check()
        ctx.log(f"[{i}/{len(ativos)}] Replicando {cod}", "step")
        time.sleep(0.35)
        ctx.progress(i / len(ativos) * 100)
    ctx.log(f"Arquivos gravados em {params['saida']}")
    return f"{len(ativos)} fluxo(s) replicado(s)."
