try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

class ErrorBrowserWidget(QWidget):
    def __init__(self):
        super(ErrorBrowserWidget, self).__init__()
        self.ly = QVBoxLayout(self)
        self.setContentsMargins(1,1,1,1)
        self.ly.setSpacing(2)
        self.hide_btn = QPushButton('Hide')
        self.ly.addWidget(self.hide_btn)
        self.hide_btn.clicked.connect(self.hide)

        self.text = QTextBrowser()
        self.text.setWordWrapMode(QTextOption.NoWrap)
        self.ly.addWidget(self.text)

    def show_error(self, text):
        self.text.setText(text)
        self.show()

    def clear(self):
        self.text.clear()
        self.hide()

