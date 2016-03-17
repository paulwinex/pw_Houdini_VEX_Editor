# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Dropbox\Dropbox\pw_pipeline\pw_pipeline\assets\houdini\python\VEX\pw_Houdini_VEX_Editor\pw_VEX_Editor\widgets\find_replace.ui'
#
# Created: Thu Mar 17 09:09:26 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_FindReplace(object):
    def setupUi(self, FindReplace):
        FindReplace.setObjectName("FindReplace")
        FindReplace.resize(403, 99)
        self.gridLayout = QtGui.QGridLayout(FindReplace)
        self.gridLayout.setObjectName("gridLayout")
        self.find_le = QtGui.QLineEdit(FindReplace)
        self.find_le.setObjectName("find_le")
        self.gridLayout.addWidget(self.find_le, 0, 0, 1, 1)
        self.find_btn = QtGui.QPushButton(FindReplace)
        self.find_btn.setObjectName("find_btn")
        self.gridLayout.addWidget(self.find_btn, 0, 1, 1, 1)
        self.replace_le = QtGui.QLineEdit(FindReplace)
        self.replace_le.setObjectName("replace_le")
        self.gridLayout.addWidget(self.replace_le, 1, 0, 1, 1)
        self.replace_btn = QtGui.QPushButton(FindReplace)
        self.replace_btn.setObjectName("replace_btn")
        self.gridLayout.addWidget(self.replace_btn, 1, 1, 1, 1)
        self.matches_lb = QtGui.QLabel(FindReplace)
        self.matches_lb.setObjectName("matches_lb")
        self.gridLayout.addWidget(self.matches_lb, 2, 0, 1, 1)
        self.replace_all_btn = QtGui.QPushButton(FindReplace)
        self.replace_all_btn.setObjectName("replace_all_btn")
        self.gridLayout.addWidget(self.replace_all_btn, 2, 1, 1, 1)

        self.retranslateUi(FindReplace)
        QtCore.QMetaObject.connectSlotsByName(FindReplace)

    def retranslateUi(self, FindReplace):
        FindReplace.setWindowTitle(QtGui.QApplication.translate("FindReplace", "Find And Replace", None, QtGui.QApplication.UnicodeUTF8))
        self.find_btn.setText(QtGui.QApplication.translate("FindReplace", "Find Next", None, QtGui.QApplication.UnicodeUTF8))
        self.replace_btn.setText(QtGui.QApplication.translate("FindReplace", "Replace Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.matches_lb.setText(QtGui.QApplication.translate("FindReplace", "Matches: 0", None, QtGui.QApplication.UnicodeUTF8))
        self.replace_all_btn.setText(QtGui.QApplication.translate("FindReplace", "Replace All", None, QtGui.QApplication.UnicodeUTF8))

