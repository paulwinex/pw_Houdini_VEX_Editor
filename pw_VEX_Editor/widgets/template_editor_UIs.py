# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Dropbox\Dropbox\pw_pipeline\pw_pipeline\assets\houdini\python\VEX\pw_VEX_Editor\widgets\template_editor.ui'
#
# Created: Sun Oct 25 01:18:32 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

class Ui_templateEditor(object):
    def setupUi(self, templateEditor):
        templateEditor.setObjectName("templateEditor")
        templateEditor.resize(631, 602)
        self.verticalLayout = QVBoxLayout(templateEditor)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QGroupBox(templateEditor)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_4.addWidget(self.label_2)
        self.verticalLayout.addWidget(self.groupBox)
        self.splitter = QSplitter(templateEditor)
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.templates_ly = QVBoxLayout(self.layoutWidget)
        self.templates_ly.setContentsMargins(0, 0, 0, 0)
        self.templates_ly.setObjectName("templates_ly")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.add_btn = QPushButton(self.layoutWidget)
        self.add_btn.setObjectName("add_btn")
        self.horizontalLayout.addWidget(self.add_btn)
        self.remove_btn = QPushButton(self.layoutWidget)
        self.remove_btn.setObjectName("remove_btn")
        self.horizontalLayout.addWidget(self.remove_btn)
        self.templates_ly.addLayout(self.horizontalLayout)
        self.templates_lw = QListWidget(self.layoutWidget)
        self.templates_lw.setObjectName("templates_lw")
        self.templates_ly.addWidget(self.templates_lw)
        self.layoutWidget1 = QWidget(self.splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_2 = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QLabel(self.layoutWidget1)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.keyword_ly = QHBoxLayout()
        self.keyword_ly.setObjectName("keyword_ly")
        self.keyword_le = QLineEdit(self.layoutWidget1)
        self.keyword_le.setObjectName("keyword_le")
        self.keyword_ly.addWidget(self.keyword_le)
        self.horizontalLayout_2.addLayout(self.keyword_ly)
        self.cursorpos_btn = QPushButton(self.layoutWidget1)
        self.cursorpos_btn.setObjectName("cursorpos_btn")
        self.horizontalLayout_2.addWidget(self.cursorpos_btn)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.text_widget_ly = QVBoxLayout()
        self.text_widget_ly.setObjectName("text_widget_ly")
        self.verticalLayout_2.addLayout(self.text_widget_ly)
        self.verticalLayout.addWidget(self.splitter)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.save_btn = QPushButton(templateEditor)
        self.save_btn.setObjectName("save_btn")
        self.horizontalLayout_4.addWidget(self.save_btn)
        self.cancel_btn = QPushButton(templateEditor)
        self.cancel_btn.setObjectName("cancel_btn")
        self.horizontalLayout_4.addWidget(self.cancel_btn)
        self.open_btn = QPushButton(templateEditor)
        self.open_btn.setObjectName("open_btn")
        self.horizontalLayout_4.addWidget(self.open_btn)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(templateEditor)
        QMetaObject.connectSlotsByName(templateEditor)
        templateEditor.setTabOrder(self.add_btn, self.remove_btn)
        templateEditor.setTabOrder(self.remove_btn, self.templates_lw)
        templateEditor.setTabOrder(self.templates_lw, self.cursorpos_btn)
        templateEditor.setTabOrder(self.cursorpos_btn, self.save_btn)
        templateEditor.setTabOrder(self.save_btn, self.cancel_btn)

    def retranslateUi(self, templateEditor):
        templateEditor.setWindowTitle(QApplication.translate("templateEditor", "Live Template Editor", None))
        self.groupBox.setTitle(QApplication.translate("templateEditor", "Info", None))
        self.label_2.setText(QApplication.translate("templateEditor", "<html><head/><body><p>Press <span style=\" font-weight:600;\">TAB</span> key after <span style=\" font-weight:600;\">keyword </span>to insert Templates into VEX Editor</p></body></html>", None))
        self.add_btn.setText(QApplication.translate("templateEditor", "Add New", None))
        self.remove_btn.setText(QApplication.translate("templateEditor", "Remove", None))
        self.label.setText(QApplication.translate("templateEditor", "Keyword", None))
        self.cursorpos_btn.setToolTip(QApplication.translate("templateEditor", "<html><head/><body><p>Set position to move cursor after apllaying template</p></body></html>", None))
        self.cursorpos_btn.setText(QApplication.translate("templateEditor", "$cursor$", None))
        self.save_btn.setText(QApplication.translate("templateEditor", "Save", None))
        self.cancel_btn.setText(QApplication.translate("templateEditor", "Cance", None))
        self.open_btn.setText(QApplication.translate("templateEditor", "Open Folder", None))

