"""Tela de abertura: mostra a configuração inicial enquanto ela acontece de verdade."""

import config
from core import aws
from core import configuracoes as cfg

from . import icons
from .qt import QtCore, QtGui, QtWidgets, Qt
from .widgets import ElidedLabel

W = QtWidgets

NAVY = "#000D3C"
NAVY_LINE = "#1A2A63"
TEXT = "#FFFFFF"
MUTED = "#97A1C2"
ORANGE = "#FF6200"
GREEN = "#45D99A"
YELLOW = "#FFB547"
RED = "#FF7474"


class SplashScreen(W.QWidget):
    """Executa as etapas uma a uma, mostrando cada uma, e depois abre a janela principal.

    Uso (main.py):
        splash = SplashScreen(criar_janela=MainWindow)
        splash.start()
    """

    PASSO_MIN_MS = 800      # tempo mínimo de cada etapa na tela (para dar para ler)
    FINAL_MS = 870          # pausa em "Tudo pronto" antes de abrir a janela

    def __init__(self, criar_janela):
        super().__init__(None, Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(700, 450)
        self._criar_janela = criar_janela
        self.janela = None
        self._etapas = [
            ("Preparando a Central", self._preparar),
            ("Conferindo as pastas de trabalho", self._pastas),
            ("Conferindo o Feeder", self._feeder),
            ("Verificando as credenciais AWS", self._aws),
            ("Carregando as telas", self._telas),
        ]
        self._i = 0
        self._montar()

    # Layout ----------------------------------------------------------------
    def _montar(self):
        lay = W.QVBoxLayout(self)
        lay.setContentsMargins(36, 32, 36, 26)
        lay.setSpacing(0)

        topo = W.QHBoxLayout()
        topo.setSpacing(14)
        logo = W.QLabel()
        pm = QtGui.QPixmap(str(config.LOGO_PATH))
        if not pm.isNull():
            pm = pm.scaled(112, 112, Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
            pm.setDevicePixelRatio(2)
            logo.setPixmap(pm)
        logo.setFixedSize(56, 56)
        topo.addWidget(logo)
        nomes = W.QVBoxLayout()
        nomes.setSpacing(2)
        nomes.addWidget(self._label("Central Eventos", f"color:{TEXT}; font-size:22px; font-weight:600;"))
        nomes.addWidget(self._label("Renda Fixa", f"color:{MUTED}; font-size:13px;"))
        topo.addLayout(nomes, 1)
        lay.addLayout(topo)

        lay.addSpacing(26)

        # Etapas já concluídas aparecem aqui, uma por linha
        self.lista = W.QVBoxLayout()
        self.lista.setSpacing(6)
        lay.addLayout(self.lista)
        lay.addStretch(1)

        self.atual = self._label("", f"color:{TEXT}; font-size:13px;")
        lay.addWidget(self.atual)
        lay.addSpacing(10)

        self.barra = W.QProgressBar()
        self.barra.setRange(0, len(self._etapas))
        self.barra.setValue(0)
        self.barra.setTextVisible(False)
        self.barra.setFixedHeight(4)
        self.barra.setStyleSheet(
            f"QProgressBar {{ background:{NAVY_LINE}; border:none; border-radius:2px; }}"
            f"QProgressBar::chunk {{ background:{ORANGE}; border-radius:2px; }}"
        )
        lay.addWidget(self.barra)
        lay.addSpacing(12)

        rodape = W.QHBoxLayout()
        self.dica = ElidedLabel("")  # corta caminhos longos no meio
        self.dica.setStyleSheet(f"color:{MUTED}; font-size:11px;")
        rodape.addWidget(self.dica, 1)
        rodape.addWidget(self._label(f"v{config.APP_VERSAO}", f"color:{MUTED}; font-size:11px;"))
        lay.addLayout(rodape)

    @staticmethod
    def _label(texto, estilo):
        lbl = W.QLabel(texto)
        lbl.setStyleSheet(estilo)
        return lbl

    def paintEvent(self, _):  # noqa: N802 - fundo azul com cantos arredondados
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        p.setPen(QtGui.QPen(QtGui.QColor(NAVY_LINE), 1))
        p.setBrush(QtGui.QColor(NAVY))
        p.drawRoundedRect(QtCore.QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 14, 14)
        # faixa laranja discreta no topo, a mesma cor do item ativo do menu
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QtGui.QColor(ORANGE))
        p.drawRoundedRect(QtCore.QRectF(36, 0, 48, 3), 1.5, 1.5)
        p.end()

    def _concluida(self, texto: str, tom: str = "ok"):
        cor, icone = {"ok": (GREEN, "check"), "warn": (YELLOW, "alert"), "error": (RED, "alert")}[tom]
        linha = W.QHBoxLayout()
        linha.setSpacing(8)
        ic = W.QLabel()
        ic.setPixmap(icons.pixmap(icone, cor, 14, 2.2))
        ic.setFixedSize(14, 14)
        linha.addWidget(ic)
        linha.addWidget(self._label(texto, f"color:{MUTED if tom == 'ok' else cor}; font-size:12px;"), 1)
        self.lista.addLayout(linha)

    # Execução --------------------------------------------------------------
    def start(self):
        tela = QtGui.QGuiApplication.primaryScreen().availableGeometry()
        self.move(tela.center() - self.rect().center())
        self.show()
        QtCore.QTimer.singleShot(150, self._proxima)

    def _proxima(self):
        if self._i >= len(self._etapas):
            self.atual.setText("Tudo pronto")
            QtCore.QTimer.singleShot(self.FINAL_MS, self._abrir)
            return
        titulo, funcao = self._etapas[self._i]
        self.atual.setText(f"{titulo}…")
        W.QApplication.processEvents()

        relogio = QtCore.QElapsedTimer()
        relogio.start()
        try:
            texto, tom = funcao()
        except Exception as exc:  # noqa: BLE001 - nunca travar a abertura
            texto, tom = f"{titulo}: {exc}", "error"
        self._concluida(texto, tom)

        self._i += 1
        self.barra.setValue(self._i)
        espera = max(0, self.PASSO_MIN_MS - relogio.elapsed())
        QtCore.QTimer.singleShot(espera, self._proxima)

    def _abrir(self):
        self.janela.show()
        self.close()

    # Etapas (cada uma devolve: texto da linha concluída, tom ok/warn/error) ---
    def _preparar(self):
        self.dica.setText(f"Pasta do programa: {cfg.pasta_raiz()}")
        return "Central iniciada", "ok"

    def _pastas(self):
        situacao = cfg.verificar()
        # garantir_pastas() também cria o Feeder; guarda se ele já existia para a próxima etapa
        self._feeder_existia = cfg.arquivo_feeder().is_file()
        criadas = cfg.garantir_pastas()
        if situacao.primeira_vez:
            return f"Primeira abertura: {len(criadas)} pastas de trabalho criadas", "ok"
        if criadas:
            return f"{len(criadas)} pasta(s) que faltavam foram recriadas", "warn"
        return "Pastas de trabalho em ordem", "ok"

    def _feeder(self):
        cfg.garantir_feeder()
        existe = cfg.arquivo_feeder().is_file()
        if existe and not getattr(self, "_feeder_existia", True):
            return "Feeder modelo criado em Config (preencha antes de processar)", "ok"
        if existe:
            return "Feeder encontrado", "ok"
        return "Feeder personalizado não encontrado (veja Configurações)", "warn"

    def _aws(self):
        if aws.existe():
            return "Credenciais AWS encontradas", "ok"
        return "Credenciais AWS não encontradas (veja a aba AWS)", "warn"

    def _telas(self):
        self.janela = self._criar_janela()
        return "Telas carregadas", "ok"
