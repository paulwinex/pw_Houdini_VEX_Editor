from PySide.QtCore import *
from PySide.QtGui import *
import select_parm_dialog_UIs
reload(select_parm_dialog_UIs)
import hqt
reload(hqt)
# style14 = hqt.get_h14_style()
vex_parms = ['snippet', 'code']
vex_sections = ['VflCode', 'OnUpdated', 'OnNameChanged', 'OnInputChanged', 'OnDeleted', 'OnCreated', 'SyncNodeVersion', 'PreFirstCreate', 'Expressions', 'OnLoaded']
fast_open_list = ['snippet', 'code', 'VflCode']

class SelectParameterDialogClass(QDialog, select_parm_dialog_UIs.Ui_Dialog):
    def __init__(self, parms, sections, node, parent):
        super(SelectParameterDialogClass, self).__init__(hqt.houWindow)
        self.setupUi(self)
        self.help_lb.setText('Select section or parameter from node:\n %s' % node.path())
        self.parms = parms
        self.sections = sections
        self.select_btn.clicked.connect(self.accept)
        self.parms_lw.itemClicked.connect(self.sections_lw.clearSelection)
        self.sections_lw.itemClicked.connect(self.parms_lw.clearSelection)
        self.show_all_cbx.clicked.connect(self.update_lists)
        self.parms_lw.itemDoubleClicked.connect(self.accept)
        self.sections_lw.itemDoubleClicked.connect(self.accept)
        # self.setStyleSheet(style14)
        self.update_lists()

    def update_lists(self):
        if self.show_all_cbx.isChecked():
            parms = self.parms.keys()
            sections = self.sections.keys()
        else:
            parms = [x for x in self.parms.keys() if x in vex_parms]
            sections = [x for x in self.sections.keys() if x in vex_sections]
        # print parms
        # print sections
        self.parms_lw.clear()
        self.parms_lw.addItems(parms)
        self.sections_lw.clear()
        self.sections_lw.addItems(sections)

    def get_data(self):
        sparm = self.parms_lw.selectedItems()
        if sparm:
            return dict(
                parm = sparm[0].text(),
                section=None
                )
        else:
            ssect = self.sections_lw.selectedItems()
            if ssect:
                return dict(
                    parm = None,
                    section=ssect[0].text()
                )


