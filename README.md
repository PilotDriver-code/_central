# Central Eventos RF (v2.3)

Reescrita da Central em **Qt 6** (PySide6), com a interface montada em código.

## Pastas de trabalho

Ficam na **raiz do programa**: ao lado do `main.py` (rodando com Python) ou ao lado do
`CentralRF.exe` (depois de empacotado). São criadas na primeira abertura e conferidas a
cada abertura e antes de cada rotina; as que faltarem são recriadas.

```
CentralRF.exe
Cravar PU\          saída do Cravar PU
Eventos SAC\        saída dos Eventos SAC
Replicar Fluxo\     saída do Replicar fluxo
Listas de ativos\   .txt usados no modo em lote
Config\             Feeder_Local.xlsx e configuracoes.json
```

Para agrupar tudo numa pasta só, troque `PASTA_DADOS = APP_DIR` por
`PASTA_DADOS = APP_DIR / "Dados"` em `config.py`.

Coloque o programa numa pasta onde o usuário pode gravar (ex.: `C:\CentralRF` ou uma
pasta de rede). Dentro de `C:\Arquivos de Programas` o Windows bloqueia a criação das pastas.

## Credenciais AWS

Sempre `C:\Users\<usuario>\.aws\credentials` (arquivo do AWS CLI). A Central só substitui
o conteúdo pela aba AWS e **nunca cria** esse arquivo: se ele não existir, o botão de
atualizar fica desativado até o AWS CLI ser configurado (`aws configure`).

## Rodar

```bash
pip install -r requirements.txt
python main.py
```

Funciona com **PySide6** (recomendado: licença LGPL, binding oficial da Qt) ou **PyQt6**.
O arquivo `app/qt.py` detecta qual está instalado; nenhum outro arquivo importa Qt diretamente.

## Estrutura

```
main.py                  ponto de entrada
config.py                nomes das pastas fixas e parâmetros das telas
app/
  qt.py                  compatibilidade PySide6 / PyQt6
  theme.py               cores (tema claro e escuro) e folha de estilo
  icons.py               ícones vetoriais coloridos pelo tema
  widgets.py             componentes: menu, interruptor, pílulas, console, avisos...
  worker.py              execução em segundo plano (QThread)
  window.py              janela principal, menu lateral, atalhos
  pages/                 uma tela por arquivo
core/
  processos.py           rotinas de processamento  <-- coloque a lógica real aqui
  aws.py                 leitura/gravação do aws.txt (sem interface)
  configuracoes.py       pastas fixas e arquivos escolhidos pelo usuário
```

## Onde plugar a lógica de verdade

As funções em `core/processos.py` **só simulam** as etapas. Troque o corpo de cada uma.
Elas rodam numa thread separada e recebem `ctx`:

```python
def cravar_pu(params, ctx):
    ctx.log("Lendo Feeder", "step")      # níveis: info, step, ok, warn, error
    df = pd.read_excel(params["feeder"])
    ctx.progress(30)                     # 0 a 100
    ctx.check()                          # para aqui se o usuário clicar em Cancelar
    ...
    return "PU cravado."                 # mensagem final no console e no aviso
```

Erros não tratados aparecem no console com o traceback e não derrubam o app.
Não acesse widgets dentro dessas funções.

## Atalhos

| Atalho          | Ação                         |
|-----------------|------------------------------|
| Ctrl+1 … Ctrl+5 | Trocar de tela (5 = Configurações) |
| Ctrl+Enter      | Executar a ação da tela      |
| Ctrl+B          | Recolher / expandir o menu   |

Tema, tela atual, tamanho da janela e estado do menu são lembrados entre aberturas.

## Gerar o .exe

No Windows, na pasta do projeto:

```
build_exe.bat
```

Sai em `dist\CentralRF.exe`. O `config.py` já distingue as duas situações:
`APP_DIR` (onde o .exe está, onde as pastas são criadas) e `RESOURCE_DIR`
(arquivos embutidos, como o logo, que o PyInstaller extrai numa pasta temporária).
