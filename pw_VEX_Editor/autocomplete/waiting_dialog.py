from PySide.QtCore import *
from PySide.QtGui import *
import hqt, hou, os
import keywords


class WaitingDialogClass(QWidget):
    main_label_text = '<b>Generate Autocompletes...<b>'
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
        self.l = QLabel(self.main_label_text)
        self.l.setAlignment(Qt.AlignCenter)
        ly.addWidget(self.l)
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
