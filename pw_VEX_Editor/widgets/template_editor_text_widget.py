try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
from vexSyntax import design, syntaxHighLighter



class TemplateEditorTextClass(QTextEdit):
    def __init__(self, parent=None, theme=None):
        super(TemplateEditorTextClass, self).__init__(parent)
        self.setAcceptRichText(False)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.colors = design.getColors(theme)
        from .. import vex_settings
        self.s = vex_settings.EditorSettingsClass()
        self.fs = 16
        self.setTheme(self.colors)

        metrics = QFontMetrics(self.document().defaultFont())
        self.setTabStopWidth(4 * metrics.width(' '))
        self.setFontSize()


        option =  self.document().defaultTextOption()
        option.setFlags(option.flags() | QTextOption.ShowTabsAndSpaces)
        option.setFlags(option.flags() | QTextOption.AddSpaceForLineAndParagraphSeparators)
        self.document().setDefaultTextOption(option)

    def setTheme(self, data=None):
        self.colors = data
        f1 = syntaxHighLighter.VEXHighlighterClass.getStyle((187,0,204), 1)
        extra =  [(r'\$cursor\$', 0, f1),]
        self.hgl = syntaxHighLighter.VEXHighlighterClass(self, data or self.colors, extra)
        self.setFontSize()

    def setFontSize(self):
        from .. import vex_settings
        bgcolor = self.colors['code']['background']
        style = self.styleSheet() +'''QTextEdit
    {
        font-size: %spx;
        color: gray;
        font-family: %s;
        background-color: rgb(%s, %s, %s);
    }''' % (self.fs,self.s.get_value('font_name',vex_settings.default_data['font_name']), bgcolor[0],bgcolor[1],bgcolor[2],)
        self.setStyleSheet(style)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.delta() > 0:
                self.fs += 1
            else:
                self.fs -= 1
            self.setFontSize()
        else:
            QTextEdit.wheelEvent(self, event)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Tab:
            self.insertPlainText('    ')
        else:
            QTextEdit.keyPressEvent(self, event)

    def insertSpecialText(self, ins, uniq=True):
        pos = self.textCursor().position()
        text = self.toPlainText()
        if uniq:
            if ins in text:
                tmp = '&**||temporarytext||**&'
                text = (text[:pos] + tmp + text[pos:]).replace(ins, '').replace(tmp, ins)
            else:
                text = text[:pos] + ins + text[pos:]
        else:
            text = text[:pos] + ins + text[pos:]
        self.setPlainText(text)
