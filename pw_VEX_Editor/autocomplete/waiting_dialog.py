from PySide.QtCore import *
from PySide.QtGui import *
import hqt, hou, os
import keywords


class WaitingDialogClass(QWidget):
    def __init__(self):
        super(WaitingDialogClass, self).__init__(hqt.houWindow)
        self.setWindowFlags(Qt.Tool)
        ly = QHBoxLayout()
        self.setLayout(ly)
        self.setWindowTitle('VEX Editor')
        try:
            t = QLabel()
            t.setPixmap(hou.ui.createQtIcon('PLAYBAR_realtime').pixmap(24,24))
            ly.addWidget(t)
        except:
            pass
        l = QLabel('Generate Autocompletes...')
        l.setAlignment(Qt.AlignCenter)
        ly.addWidget(l)
        self.resize(100,100)
        if hqt.houWindow:
            g = self.geometry()
            g.moveCenter(hqt.houWindow.geometry().center())
            self.setGeometry(g)

    def generate(self):
        if not os.path.exists(keywords.vex_settings.get_autocomplete_cache_file()):
            self.setStyleSheet(hqt.get_h14_style())
            self.show()
        # small pause to update ui
        QTimer.singleShot(200, self.do_generate)

    def do_generate(self):
        keywords.generate_completes()
        self.close()