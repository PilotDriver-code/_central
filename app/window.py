import config
from core import configuracoes as cfg

from . import theme
from .pages import PAGES, ConfiguracoesPage
from .qt import QtCore, QtGui, QtWidgets, Qt, Signal
from .widgets import IconButton, NavButton, Toast, label

W = QtWidgets


class Sidebar(W.QFrame):
    EXPANDED = 236
    COLLAPSED = 72

    page_requested = Signal(int)

    def __init__(self, pages, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.collapsed = False
        self.setFixedWidth(self.EXPANDED)

        lay = W.QVBoxLayout(self)
        lay.setContentsMargins(16, 18, 16, 16)
        lay.setSpacing(4)

        # Marca
        brand = W.QHBoxLayout()
        brand.setSpacing(12)
        logo = W.QLabel()
        pm = QtGui.QPixmap(str(config.LOGO_PATH))
        if not pm.isNull():
            dpr = self.devicePixelRatioF() or 1.0
            pm = pm.scaled(int(40 * max(dpr, 2)), int(40 * max(dpr, 2)),
                           Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
            pm.setDevicePixelRatio(max(dpr, 2))
            logo.setPixmap(pm)
        logo.setFixedSize(40, 40)
        brand.addWidget(logo)
        self.brand_text = W.QWidget()
        bt = W.QVBoxLayout(self.brand_text)
        bt.setContentsMargins(0, 0, 0, 0)
        bt.setSpacing(0)
        bt.addWidget(label("Central Eventos", "BrandName"))
        bt.addWidget(label("Renda Fixa", "BrandSub"))
        brand.addWidget(self.brand_text, 1)
        lay.addLayout(brand)
        lay.addSpacing(20)

        sep = W.QFrame()
        sep.setObjectName("NavSep")
        lay.addWidget(sep)
        lay.addSpacing(12)

        # Navegação (telas com nav_bottom=True vão para o rodapé)
        self.nav_buttons: list[NavButton] = []
        bottom = []
        for i, page in enumerate(pages):
            b = NavButton(page.nav_label, page.nav_icon)
            b.clicked.connect(lambda _=False, idx=i: self.page_requested.emit(idx))
            self.nav_buttons.append(b)
            if getattr(page, "nav_bottom", False):
                bottom.append(b)
            else:
                lay.addWidget(b)

        lay.addStretch(1)
        for b in bottom:
            lay.addWidget(b)
        if bottom:
            sep2 = W.QFrame()
            sep2.setObjectName("NavSep")
            lay.addSpacing(8)
            lay.addWidget(sep2)
            lay.addSpacing(8)

        self.btn_toggle = NavButton("Recolher menu", "chevrons-left", checkable=False)
        self.btn_toggle.clicked.connect(self.toggle)
        lay.addWidget(self.btn_toggle)
        self.btn_exit = NavButton("Sair", "logout", checkable=False)
        lay.addWidget(self.btn_exit)

        self._all_buttons = self.nav_buttons + [self.btn_toggle, self.btn_exit]
        for b in self._all_buttons:
            b.set_collapsed(False)

        self._anim = QtCore.QParallelAnimationGroup(self)
        for prop in (b"minimumWidth", b"maximumWidth"):
            a = QtCore.QPropertyAnimation(self, prop)
            a.setDuration(200)
            a.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)
            self._anim.addAnimation(a)
        self._anim.finished.connect(self._after_anim)

    def set_current(self, idx: int):
        self.nav_buttons[idx].setChecked(True)

    def set_collapsed(self, collapsed: bool, animate: bool = True):
        if collapsed == self.collapsed:
            return
        self.collapsed = collapsed
        start, end = (self.EXPANDED, self.COLLAPSED) if collapsed else (self.COLLAPSED, self.EXPANDED)
        if collapsed:  # some com o texto antes de encolher
            self._apply_text(True)
        if not animate:
            self.setFixedWidth(end)
            self._after_anim()
            return
        for i in range(self._anim.animationCount()):
            a = self._anim.animationAt(i)
            a.setStartValue(start)
            a.setEndValue(end)
        self._anim.start()

    def toggle(self):
        self.set_collapsed(not self.collapsed)

    def _apply_text(self, collapsed: bool):
        self.brand_text.setVisible(not collapsed)
        for b in self._all_buttons:
            b.set_collapsed(collapsed)
        self.btn_toggle._label = "Expandir menu" if collapsed else "Recolher menu"
        self.btn_toggle._icon_name = "chevrons-right" if collapsed else "chevrons-left"
        self.btn_toggle.refresh_icons()
        self.btn_toggle.set_collapsed(collapsed)

    def _after_anim(self):
        if not self.collapsed:  # texto volta só quando já há espaço
            self._apply_text(False)

    def refresh_icons(self):
        for b in self._all_buttons:
            b.refresh_icons()


class MainWindow(W.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.APP_NOME)
        self.setWindowIcon(QtGui.QIcon(str(config.LOGO_PATH)))
        self.setMinimumSize(1080, 680)
        self.settings = QtCore.QSettings("CentralRF", "CentralEventos")

        central = W.QWidget()
        root = W.QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setCentralWidget(central)

        self.sidebar = Sidebar(PAGES)
        self.sidebar.page_requested.connect(self.go_to)
        self.sidebar.btn_exit.clicked.connect(self.close)
        root.addWidget(self.sidebar)

        content = W.QFrame()
        content.setObjectName("Content")
        content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        c = W.QVBoxLayout(content)
        c.setContentsMargins(32, 26, 32, 28)
        c.setSpacing(22)

        # Cabeçalho
        head = W.QHBoxLayout()
        head.setSpacing(12)
        titles = W.QVBoxLayout()
        titles.setSpacing(4)
        self.lbl_title = label("", "PageTitle")
        self.lbl_desc = label("", "PageDesc")
        titles.addWidget(self.lbl_title)
        titles.addWidget(self.lbl_desc)
        head.addLayout(titles, 1)
        self.btn_theme = IconButton("moon", "Alternar tema claro/escuro", size=20)
        self.btn_theme.clicked.connect(self.toggle_theme)
        head.addWidget(self.btn_theme, 0, Qt.AlignmentFlag.AlignTop)
        c.addLayout(head)

        # Telas
        self.stack = W.QStackedWidget()
        self.pages = [P() for P in PAGES]
        for p in self.pages:
            self.stack.addWidget(p)
        c.addWidget(self.stack, 1)
        root.addWidget(content, 1)

        self._shortcuts()
        self._restore()
        # Conferência das pastas logo depois que a janela aparecer.
        QtCore.QTimer.singleShot(250, self._check_setup)

    # Navegação --------------------------------------------------------------
    def go_to(self, idx: int):
        page = self.pages[idx]
        self.stack.setCurrentIndex(idx)
        self.sidebar.set_current(idx)
        self.lbl_title.setText(page.title)
        self.lbl_desc.setText(page.description)
        page.on_shown()
        self.settings.setValue("page", idx)

    def go_to_settings(self):
        for i, p in enumerate(self.pages):
            if isinstance(p, ConfiguracoesPage):
                self.go_to(i)
                return

    def _check_setup(self):
        """Na abertura: cria as pastas de trabalho que faltarem (ao lado do .exe)."""
        situacao = cfg.verificar()
        if not situacao.pastas_faltando:
            return
        try:
            criadas = cfg.garantir_pastas()
        except OSError as exc:
            self.go_to_settings()
            Toast.show_message(self.centralWidget(),
                               f"Não foi possível criar as pastas em {cfg.pasta_raiz()}: {exc}", "error")
            return
        if situacao.primeira_vez:
            Toast.show_message(self.centralWidget(), "Pastas de trabalho criadas junto do programa.", "ok")
        else:
            Toast.show_message(self.centralWidget(),
                               f"{len(criadas)} subpasta(s) que faltavam foram recriadas.", "warn")
        self.stack.currentWidget().on_shown()

    def _shortcuts(self):
        for i in range(len(self.pages)):
            sc = QtGui.QShortcut(QtGui.QKeySequence(f"Ctrl+{i + 1}"), self)
            sc.activated.connect(lambda idx=i: self.go_to(idx))
        for seq in ("Ctrl+Return", "Ctrl+Enter"):
            sc = QtGui.QShortcut(QtGui.QKeySequence(seq), self)
            sc.activated.connect(lambda: self.stack.currentWidget().run())
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+B"), self).activated.connect(self.sidebar.toggle)

    # Tema -------------------------------------------------------------------
    def apply_theme(self, name: str):
        theme.set_theme(name)
        W.QApplication.instance().setStyleSheet(theme.build_qss())
        self.btn_theme.set_icon_name("sun" if name == "dark" else "moon")
        self.sidebar.refresh_icons()
        for p in self.pages:
            p.refresh_icons()
        self.settings.setValue("theme", name)

    def toggle_theme(self):
        self.apply_theme("light" if theme.name() == "dark" else "dark")

    # Estado -----------------------------------------------------------------
    def _restore(self):
        self.apply_theme(str(self.settings.value("theme", "light")))
        geo = self.settings.value("geometry")
        if geo is not None:
            self.restoreGeometry(geo)
        else:
            self.resize(1200, 760)
        if str(self.settings.value("collapsed", "false")).lower() == "true":
            self.sidebar.set_collapsed(True, animate=False)
        try:
            idx = int(self.settings.value("page", 0))
        except (TypeError, ValueError):
            idx = 0
        self.go_to(idx if 0 <= idx < len(self.pages) else 0)

    def closeEvent(self, event):  # noqa: N802
        busy = [p for p in self.pages if p.is_busy()]
        if busy:
            r = W.QMessageBox.question(
                self, "Rotina em andamento",
                f"{busy[0].title} ainda está rodando. Fechar mesmo assim?",
            )
            if r != W.QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            for p in busy:
                p.cancel()
                p._thread.wait(3000)
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("collapsed", self.sidebar.collapsed)
        super().closeEvent(event)
