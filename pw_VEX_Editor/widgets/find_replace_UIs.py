# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Dropbox\Dropbox\pw_pipeline\pw_pipeline\assets\houdini\python\VEX\pw_Houdini_VEX_Editor\pw_VEX_Editor\widgets\find_replace.ui'
#
# Created: Thu Mar 17 09:09:26 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

class Ui_FindReplace(object):
    def setupUi(self, FindReplace):
        FindReplace.setObjectName("FindReplace")
        FindReplace.resize(403, 99)
        self.gridLayout = QGridLayout(FindReplace)
        self.gridLayout.setObjectName("gridLayout")
        self.find_le = QLineEdit(FindReplace)
        self.find_le.setObjectName("find_le")
        self.gridLayout.addWidget(self.find_le, 0, 0, 1, 1)
        self.find_btn = QPushButton(FindReplace)
        self.find_btn.setObjectName("find_btn")
        self.gridLayout.addWidget(self.find_btn, 0, 1, 1, 1)
        self.replace_le = QLineEdit(FindReplace)
        self.replace_le.setObjectName("replace_le")
        self.gridLayout.addWidget(self.replace_le, 1, 0, 1, 1)
        self.replace_btn = QPushButton(FindReplace)
        self.replace_btn.setObjectName("replace_btn")
        self.gridLayout.addWidget(self.replace_btn, 1, 1, 1, 1)
        self.matches_lb = QLabel(FindReplace)
        self.matches_lb.setObjectName("matches_lb")
        self.gridLayout.addWidget(self.matches_lb, 2, 0, 1, 1)
        self.replace_all_btn = QPushButton(FindReplace)
        self.replace_all_btn.setObjectName("replace_all_btn")
        self.gridLayout.addWidget(self.replace_all_btn, 2, 1, 1, 1)

        self.retranslateUi(FindReplace)
        QMetaObject.connectSlotsByName(FindReplace)

    def retranslateUi(self, FindReplace):
        FindReplace.setWindowTitle(QApplication.translate("FindReplace", "Find And Replace", None))
        self.find_btn.setText(QApplication.translate("FindReplace", "Find Next", None))
        self.replace_btn.setText(QApplication.translate("FindReplace", "Replace Selected", None))
        self.matches_lb.setText(QApplication.translate("FindReplace", "Matches: 0", None))
        self.replace_all_btn.setText(QApplication.translate("FindReplace", "Replace All", None))

