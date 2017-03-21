try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
import find_replace_UIs
reload(find_replace_UIs)
from ..icons import icons
reload(icons)

class FindReplaceDialog(QDialog, find_replace_UIs.Ui_FindReplace):
    closed = Signal()
    def __init__(self, editor, parent):
        super(FindReplaceDialog, self).__init__(parent)
        self.setupUi(self)
        # self.setWindowIcon(QIcon(icons.icons['houdini']))
        self.setWindowFlags(Qt.Tool)
        self.editor = editor
        self.lastSearch = dict(
            index=0,
            reqest=None
        )
        self.find_btn.clicked.connect(self.find)
        # self.find_le.returnPressed.connect(self.find_by_return)
        self.find_le.textChanged.connect(self.find_matches)
        self.replace_btn.clicked.connect(self.replace)
        self.replace_le.returnPressed.connect(self.replace)
        self.replace_all_btn.clicked.connect(self.replaceAll)

        self.setFixedSize(400,100)

    def closeEvent(self, event):
        self.closed.emit()
        super(FindReplaceDialog, self).closeEvent(event)

    def find_matches(self, txt):
        txt = txt or self.find_le.text()
        if txt:
            count = self.editor.toPlainText().count(txt)
            self.matches_lb.setText('Match: %s' % count)
        else:
            self.matches_lb.setText('Match: 0')

    def find(self):
        source = self.find_le.text()
        if not source:return
        count = self.editor.toPlainText().count(source)
        if not count:
            c = self.editor.textCursor()
            c.clearSelection()
            self.editor.setTextCursor(c)
        else:
            if not source == self.lastSearch['reqest']:
                self.lastSearch = {'reqest':source, 'index':0}
            self.lastSearch['index'] = self.editor.select_word(source, self.lastSearch['index'])

    def replace(self):
        target = self.replace_le.text()
        l = self.editor.replace_selected(target)
        if not l is None:
            self.lastSearch['index'] -= len(target)

    def replaceAll(self):
        source = self.find_le.text()
        if source:
            target = self.replace_le.text()
            self.editor.replace_all(source, target)