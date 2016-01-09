from PySide.QtCore import *
from PySide.QtGui import *
import hou, os
from .. autocomplete import vex_parser
from vexSyntax import design
reload(design)
reload(vex_parser)



class CompleterListClass(QListWidget):
    def __init__(self, parent=None, editor=None):
        super(CompleterListClass, self).__init__(parent)
        self.setAlternatingRowColors(1)
        self.lineHeight = 18
        self.e = editor
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWindowFlags(Qt.FramelessWindowHint |  Qt.Window | Qt.WindowStaysOnTopHint)
        # self.setStyleSheet(hqt.get_h14_style(parent.theme))
        self.currentItemChanged.connect(self.highlight_item)
        self.itemDoubleClicked.connect(self.apply_current_complete)
        # self.updateStyle()

    def updateStyle(self, colors=None):
        if not colors:
            colors = design.getColors()
        self.colors = {
            vex_parser.wordCompletion.FUNCTION: colors['completer']['methods'],
            vex_parser.wordCompletion.ATTRIBUTE: colors['completer']['attribute'],
            vex_parser.wordCompletion.TYPE: colors['completer']['type'],
            vex_parser.wordCompletion.DEFINITION: colors['completer']['directive'],
            vex_parser.wordCompletion.KEYWORD: colors['completer']['keywords'],
            vex_parser.wordCompletion.VARIABLE: colors['completer']['variable'],
            'selected': colors['completer']['background_selected'],
            'bg': colors['completer']['background']
        }

        self.setStyleSheet('background-color: rgb(%s,%s,%s);' % (colors['completer']['background'][0],
                                                                 colors['completer']['background'][1],
                                                                 colors['completer']['background'][2]
                                                                ))

    def highlight_item(self, new, old):
        if old:
            w = self.itemWidget(old)
            if w: w.off()
        if new:
            w = self.itemWidget(new)
            if w:
                w.on()

    def update_complete_list(self, names=None):
        self.clear()
        if names:
            for i, n in enumerate(names):
                item = QListWidgetItem(self)
                # h14
                if hou.applicationVersion()[0] <= 14:
                    label = CompleterLabel(n, i%2, self)
                    self.setItemWidget(item, label)
                else:
                # h15
                    item.setText(n.name)

                item.setData(32, n)
                self.addItem(item)
            self.setCurrentRow(0)
            self.showMe()
        else:
            self.hideMe()
        self.e.update()

    def apply_current_complete(self):
        i = self.selectedItems()
        if i:
            comp = i[0].data(32)
            self.sendText(comp)
        self.hideMe()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()
            self.editor().setFocus()
        # elif event.text():
        #     self.editor().setFocus()
        elif key in [Qt.Key_Return , Qt.Key_Enter]:
            self.editor().setFocus()
            self.apply_current_complete()
            return event
        elif key == Qt.Key_Up:
            sel = self.selectedItems()
            if sel:
                i = self.row(sel[0])
                if i == 0:
                    QListWidget.keyPressEvent(self, event)
                    self.setCurrentRow(self.count()-1)
                    return
        elif key == Qt.Key_Down:
            sel = self.selectedItems()
            if sel:
                i = self.row(sel[0])
                if i+1 == self.count():
                    QListWidget.keyPressEvent(self, event)
                    self.setCurrentRow(0)
                    return
        elif key in [Qt.Key_Backspace, Qt.Key_Left, Qt.Key_Right]:
            self.editor().setFocus()
            self.editor().activateWindow()
            self.editor().keyPressEvent(event)
        elif event.text():
            self.editor().keyPressEvent(event)
            return

        QListWidget.keyPressEvent(self, event)

    def sendText(self, comp):
        self.editor().insert_text(comp)

    def editor(self):
        return self.e

    def activateCompleter(self, key=False):
        self.activateWindow()
        if not key==Qt.Key_Up:
            self.setCurrentRow(min(1, self.count()-1))
        else:
            self.setCurrentRow(self.count()-1)

    def showMe(self):
        self.show()
        self.e.move_completer()
        # self.e.update()

    def hideMe(self):
        self.hide()
        if not os.name == 'nt':
            def activateditor():
                self.e.activateWindow()
                self.e.setFocus()
            QTimer.singleShot(100, activateditor)
        # self.e.update()

    # def viewportEvent(self, event):
    #     return QListWidget.viewportEvent(self, event)

    def focusOutEvent(self, event):
        self.hideMe()
        QListWidget.focusOutEvent(self, event)


class CompleterLabel(QLabel):
    style='''
    background-color: rgb{bgcolor};
    color: rgb{color};
    font-size:14px;
    border: none;
    padding: 0px 15px 0px 0px;
    '''
    def __init__(self, comp, alternate=0, parent=None):
        super(CompleterLabel, self).__init__()
        self.par = parent
        self.a = alternate
        self.setText(comp.name)
        self.type = comp.type
        self.off()

    def on(self):
        # return
        s = self.style.format(bgcolor=tuple(self.par.colors['selected']),
                              color=(255,255,255))

        self.setStyleSheet(s)

    def off(self):
        # return
        s = self.style.format(bgcolor=tuple(self.par.colors['bg']),
                              color=tuple(self.par.colors[self.type]))
        self.setStyleSheet(s)
