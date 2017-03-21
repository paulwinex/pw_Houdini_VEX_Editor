try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
from ..autocomplete import keywords
from input_widget import maximumFontSize, minimumFontSize, design, syntaxHighLighter



class HelpWindow(QWidget):
    def __init__(self, parent):
        super(HelpWindow, self).__init__(parent)
        self.ly = QHBoxLayout()
        self.setLayout(self.ly)
        self.ly.setContentsMargins(1,1,1,1)
        self.ly.setSpacing(2)
        self.bg = [0,0,0]
        self.last = ''
        self.pinned = False
        self.valid = False
        self.timer = QTimer()
        from .. import vex_settings
        self.s = vex_settings.EditorSettingsClass()
        self.fs = self.s.get_value('help_font_size',vex_settings.default_data['help_font_size'])
        self.fn = self.s.get_value('font_name',vex_settings.default_data['font_name'])
        self.setTextEditFontSize()
        self.out = QTextBrowser()
        self.out.setWordWrapMode(QTextOption.NoWrap)
        self.ly.addWidget(self.out)

        self.btn_ly = QVBoxLayout()
        self.ly.addLayout(self.btn_ly)
        self.pin_btn = QPushButton('o')
        self.pin_btn.setToolTip('Pin Help Window')
        self.pin_btn.setMaximumSize(QSize(20,20))
        self.pin_btn.setCheckable(1)
        @self.pin_btn.clicked.connect
        def change_pin():
            self.pinned = self.pin_btn.isChecked()
            self.pin_act.setChecked(self.pinned)

        self.btn_ly.addWidget(self.pin_btn)
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.btn_ly.addItem(spacerItem)
        self.create_menu()
        if not keywords.functions_help:
            self.out.setText('<b>Context help not available</b>')
        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.open_menu)


    def show_help(self, text=''):
        if not self.isVisible():
            return
        if not self.visibleRegion():
            return
        if text and not isinstance(text, int):
            if not self.pinned:# and bool(self.out.toPlainText()):
                if not self.last == text:
                    self.out.setText(text)
                    # self.show()
                    # height = len(text.split('<br>'))
                    # self.setMaximumHeight(min(int((self.fs * height)+self.fs), 200))
                    self.last = text
        else:
            if not self.pinned:
                self.out.setText('')
            # self.hide()

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.delta() > 0:
                self.changeFontSize(True)
            else:
                self.changeFontSize(False)
        else:
            super(HelpWindow, self).wheelEvent(event)

    def changeFontSize(self, up):
        if up:
            self.fs = min(maximumFontSize, self.fs+1)
        else:
            self.fs = max(minimumFontSize, self.fs - 1)
        self.setTextEditFontSize(self.fs)
        self.messageSignal.emit('Font Size: %s' % self.fs)

    def setTextEditFontSize(self, size=None):
        size = size or self.fs
        style = self.styleSheet() +'''QTextEdit
    {
        font-size: %spx;
        font-family: %s;
        background-color: rgb(%s, %s, %s);
    }''' % (size, self.fn, self.bg[0],self.bg[1],self.bg[2],)
        self.setStyleSheet(style)

    def apply_style(self, theme=None, colors=None):
        # get style
        if not colors:
            colors = design.getColors(theme)

        # editor bg
        color = colors['code']['background']
        self.bg = color
        self.setTextEditFontSize()
        # syntax hightlighter
        self.blockSignals(True)
        # colors = None
        self.hgl = syntaxHighLighter.VEXHighlighterClass(self.out, colors, skip_lines=1)
        self.blockSignals(False)

    def hide_me(self):
        self.timer.singleShot(100, self.hide)

    def show(self, *args, **kwargs):
        if self.timer.isActive():
            self.timer.stop()
        super(HelpWindow, self).show(*args, **kwargs)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.open_menu(event)
        else:
            super(HelpWindow, self).mousePressEvent(event)

    def open_menu(self, event):
        a = self.menu.exec_(event.globalPos())
        if a:
            if a is self.hide_act:
                # self.pin_btn.setChecked(self.pin_btn.isChecked())
                self.hide_me()
            elif a is self.pin_act:
                self.pinned = self.pin_act.isChecked()
                self.pin_btn.setChecked(self.pinned)
            else:
                name = a.text()
                if name:
                    self.show_help(keywords.get_functions_help_window(name))

    def create_menu(self):
        keywords.get_functions_help_window('')
        self.menu = QMenu(self)
        self.hide_act = QAction('Hide', self, triggered=self.hide_me)
        self.menu.addAction(self.hide_act)
        self.pin_act = QAction('Pin', self, checkable=True)
        self.menu.addAction(self.pin_act)
        return
        self.menu.addSeparator()
        funcmenu = QMenu('Show Function', self)
        self.menu.addMenu(funcmenu)
        if keywords.functions_help:
            funcs = keywords.functions_help.keys()
            titles = list(set([x[0] for x in funcs]))
            titles = {x.title():[] for x in titles}
            for f in funcs:
                titles[f[0].title()].append(f)
            if titles:
                for M, ff in sorted(titles.items(), key=lambda x:x):
                    sub = QMenu(M, self)
                    for f in ff:
                        sub.addAction(QAction(f, self))
                    funcmenu.addMenu(sub)
            else:
                funcmenu.addAction(QAction('Empty', self, enabled=False))
        else:
            funcmenu.addAction(QAction('Empty', self, enabled=False))

    def toggle_visible(self):
        if self.isVisible():
            # self.hide()
            return False
        else:
            # self.show()
            return True