from PySide.QtCore import *
from PySide.QtGui import *

from input_widget import maximumFontSize, minimumFontSize, vex_settings, design, syntaxHighLighter

class HelpWindow(QWidget):
    def __init__(self, parent):
        super(HelpWindow, self).__init__(parent)
        self.ly = QVBoxLayout()
        self.setLayout(self.ly)
        self.ly.setContentsMargins(1,1,1,1)
        self.ly.setSpacing(2)
        self.bg = [0,0,0]
        self.last = ''
        self.s = vex_settings.EditorSettingsClass()
        self.fs = self.s.get_value('help_font_size',vex_settings.default_data['help_font_size'])
        self.fn = self.s.get_value('font_name',vex_settings.default_data['font_name'])
        self.setTextEditFontSize()
        self.out = QTextBrowser()
        self.out.setWordWrapMode(QTextOption.NoWrap)
        self.ly.addWidget(self.out)

    def show_help(self, text=''):
        if text and not isinstance(text, int):
            if not self.last == text:
                self.out.setText(text)
            self.show()
            height = len(text.split('<br>'))
            self.setMaximumHeight(min(int((self.fs * height)+self.fs), 200))
        else:
            self.out.setText('')
            self.hide()

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
