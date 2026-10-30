from datetime import date, timedelta

import config
from core import configuracoes as cfg
from core import processos

from ..qt import QtCore, QtWidgets, Qt
from ..widgets import Field, hline, label, repolish
from .base import BasePage

W = QtWidgets


def _qdate(d: date) -> QtCore.QDate:
    return QtCore.QDate(d.year, d.month, d.day)


def _pydate(q: QtCore.QDate) -> date:
    return date(q.year(), q.month(), q.day())


class EventosSACPage(BasePage):
    title = "Eventos SAC"
    description = "Exporte os eventos do SAC de um período."
    nav_icon = "calendar"
    nav_label = "Eventos SAC"

    def __init__(self, parent=None):
        super().__init__(parent)
        form = self.build_split("Período", "Processar")

        hoje = date.today()
        self.dt_ini = self._date_edit(hoje)
        self.dt_fim = self._date_edit(hoje)
        row = W.QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(Field("Data início", self.dt_ini), 1)
        row.addWidget(Field("Data final", self.dt_fim), 1)
        form.addLayout(row)

        presets = W.QHBoxLayout()
        presets.setSpacing(4)
        presets.addWidget(label("Atalhos:", "Hint"))
        for text, fn in (
            ("Hoje", lambda: (hoje, hoje)),
            ("Últimos 7 dias", lambda: (hoje - timedelta(days=6), hoje)),
            ("Mês atual", lambda: (hoje.replace(day=1), hoje)),
        ):
            b = W.QPushButton(text)
            b.setObjectName("LinkButton")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _=False, f=fn: self._apply_range(*f()))
            presets.addWidget(b)
        presets.addStretch(1)
        form.addLayout(presets)

        self.f_range = label("", "Hint")
        self.f_range.hide()
        form.addWidget(self.f_range)

        form.addWidget(hline())

        form.addWidget(self.fixed_path_field("Pasta de saída", lambda: cfg.pasta("eventos_sac")))

        self.dt_ini.dateChanged.connect(self._validate)
        self.dt_fim.dateChanged.connect(self._validate)

    def _date_edit(self, d: date) -> W.QDateEdit:
        e = W.QDateEdit()
        e.setCalendarPopup(True)
        e.setDisplayFormat("dd/MM/yyyy")
        e.setMinimumDate(_qdate(config.DATA_MINIMA_EVENTOS))
        e.setDate(_qdate(max(d, config.DATA_MINIMA_EVENTOS)))
        return e

    def _apply_range(self, ini: date, fim: date):
        self.dt_ini.setDate(_qdate(ini))
        self.dt_fim.setDate(_qdate(fim))

    def _validate(self) -> bool:
        ini, fim = _pydate(self.dt_ini.date()), _pydate(self.dt_fim.date())
        ok = fim >= ini
        self.dt_fim.setProperty("invalid", not ok)
        repolish(self.dt_fim)
        if ok:
            dias = (fim - ini).days + 1
            self.f_range.setText(f"{dias} dia" + ("s" if dias > 1 else "") + " no período")
            self.f_range.setProperty("tone", "")
        else:
            self.f_range.setText("A data final precisa ser igual ou posterior à data de início.")
            self.f_range.setProperty("tone", "error")
        repolish(self.f_range)
        self.f_range.show()
        return ok

    def run(self):
        if not self.ensure_ready():
            return
        if not self._validate():
            self.toast("Ajuste o período antes de processar.", "error")
            return
        params = {
            "inicio": _pydate(self.dt_ini.date()),
            "fim": _pydate(self.dt_fim.date()),
            "saida": str(cfg.pasta("eventos_sac")),
        }
        self.start_task(processos.eventos_sac, params, "Eventos SAC")
