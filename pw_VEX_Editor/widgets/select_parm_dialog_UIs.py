# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Dropbox\Dropbox\pw_pipeline\pw_pipeline\assets\houdini\python\VEX\pw_VEX_Editor\widgets\select_parm_dialog.ui'
#
# Created: Tue Sep 08 10:35:14 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(389, 390)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.help_lb = QtGui.QLabel(Dialog)
        self.help_lb.setObjectName("help_lb")
        self.verticalLayout.addWidget(self.help_lb)
        self.show_all_cbx = QtGui.QCheckBox(Dialog)
        self.show_all_cbx.setObjectName("show_all_cbx")
        self.verticalLayout.addWidget(self.show_all_cbx)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setContentsMargins(3, -1, 3, 3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.parms_lw = QtGui.QListWidget(self.groupBox)
        self.parms_lw.setObjectName("parms_lw")
        self.verticalLayout_2.addWidget(self.parms_lw)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setContentsMargins(3, -1, 3, 3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.sections_lw = QtGui.QListWidget(self.groupBox_2)
        self.sections_lw.setObjectName("sections_lw")
        self.verticalLayout_3.addWidget(self.sections_lw)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.select_btn = QtGui.QPushButton(Dialog)
        self.select_btn.setObjectName("select_btn")
        self.verticalLayout.addWidget(self.select_btn)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Select parameret or section to edit", None, QtGui.QApplication.UnicodeUTF8))
        self.help_lb.setText(QtGui.QApplication.translate("Dialog", "Select section or parameter from node:", None, QtGui.QApplication.UnicodeUTF8))
        self.show_all_cbx.setText(QtGui.QApplication.translate("Dialog", "Show all parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "String Parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "Sections", None, QtGui.QApplication.UnicodeUTF8))
        self.select_btn.setText(QtGui.QApplication.translate("Dialog", "Select", None, QtGui.QApplication.UnicodeUTF8))

