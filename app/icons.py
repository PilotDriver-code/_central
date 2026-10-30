"""Ícones vetoriais (SVG) desenhados em linha, coloridos em tempo de execução.

Por serem vetoriais, ficam nítidos em qualquer escala de tela (125%, 150%...)
e mudam de cor junto com o tema — sem precisar de um PNG por cor.
"""

from .qt import QtCore, QtGui, QtSvg

_PATHS = {
    "banknote": '<rect x="2.5" y="6" width="19" height="12" rx="2"/>'
                '<circle cx="12" cy="12" r="2.6"/><path d="M6 9.5h.01M18 14.5h.01"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15" rx="2"/>'
                '<path d="M3.5 10h17M8 3v4M16 3v4M8 14h.01M12 14h.01M16 14h.01M8 17h.01M12 17h.01"/>',
    "repeat": '<path d="M17 2.5l3 3-3 3"/><path d="M4 11.5v-1a5 5 0 0 1 5-5h11"/>'
              '<path d="M7 21.5l-3-3 3-3"/><path d="M20 12.5v1a5 5 0 0 1-5 5H4"/>',
    "cloud": '<path d="M7 18.5h10.5a4 4 0 0 0 .6-7.95A6 6 0 0 0 6.6 9.1 4.7 4.7 0 0 0 7 18.5z"/>',
    "logout": '<path d="M14 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4"/><path d="M10 16l-4-4 4-4M6 12h10"/>',
    "chevrons-left": '<path d="M11 17l-5-5 5-5M18 17l-5-5 5-5"/>',
    "chevrons-right": '<path d="M13 17l5-5-5-5M6 17l5-5-5-5"/>',
    "chevron-down": '<path d="M6 9l6 6 6-6"/>',
    "folder": '<path d="M3.5 7a2 2 0 0 1 2-2h4l2 2.5h7a2 2 0 0 1 2 2V17a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z"/>',
    "file": '<path d="M14 3.5H7a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8.5z"/><path d="M14 3.5v5h5"/>',
    "sun": '<circle cx="12" cy="12" r="4"/>'
           '<path d="M12 2.5v2M12 19.5v2M4.6 4.6L6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4L6 18M18 6l1.4-1.4"/>',
    "moon": '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    "play": '<path d="M8 5.5v13l10-6.5z" fill="{c}"/>',
    "trash": '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4.5h6V7"/>',
    "copy": '<rect x="8.5" y="8.5" width="12" height="12" rx="2"/>'
            '<path d="M15.5 8.5v-3a2 2 0 0 0-2-2h-8a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h3"/>',
    "external": '<path d="M14 4h6v6M20 4l-9 9M18 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "x": '<path d="M6 6l12 12M18 6L6 18"/>',
    "alert": '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.5M12 16.5h.01"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5.5M12 7.5h.01"/>',
    "save": '<path d="M5 20h14M12 4v11M7 10l5 5 5-5"/>',
    "settings": '<circle cx="12" cy="12" r="3"/>'
                '<path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 '
                '1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1'
                'a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1'
                'a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9'
                'a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1'
                'a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1'
                'a1.7 1.7 0 0 0-1.5 1z"/>',
    "rotate": '<path d="M3.5 12a8.5 8.5 0 0 1 14.5-6L20.5 8.5"/><path d="M20.5 3.5v5h-5"/>'
              '<path d="M20.5 12a8.5 8.5 0 0 1-14.5 6L3.5 15.5"/><path d="M3.5 20.5v-5h5"/>',
    "stop": '<rect x="6.5" y="6.5" width="11" height="11" rx="2"/>',
}


def svg(name: str, color: str, stroke: float = 1.8) -> str:
    body = _PATHS[name].replace("{c}", color)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" '
        f'stroke-linejoin="round">{body}</svg>'
    )


def pixmap(name: str, color: str, size: int = 20, stroke: float = 1.8) -> QtGui.QPixmap:
    screen = QtGui.QGuiApplication.primaryScreen()
    dpr = max(2.0, screen.devicePixelRatio() if screen else 1.0)
    renderer = QtSvg.QSvgRenderer(QtCore.QByteArray(svg(name, color, stroke).encode()))
    pm = QtGui.QPixmap(int(size * dpr), int(size * dpr))
    pm.fill(QtCore.Qt.GlobalColor.transparent)
    p = QtGui.QPainter(pm)
    renderer.render(p)
    p.end()
    pm.setDevicePixelRatio(dpr)
    return pm


def icon(name: str, color: str, color_on: str | None = None, size: int = 20,
         disabled: str | None = None) -> QtGui.QIcon:
    ic = QtGui.QIcon()
    M, S = QtGui.QIcon.Mode, QtGui.QIcon.State
    ic.addPixmap(pixmap(name, color, size), M.Normal, S.Off)
    ic.addPixmap(pixmap(name, color_on or color, size), M.Normal, S.On)
    ic.addPixmap(pixmap(name, color_on or color, size), M.Active, S.On)
    if disabled:
        ic.addPixmap(pixmap(name, disabled, size), M.Disabled, S.Off)
    return ic
