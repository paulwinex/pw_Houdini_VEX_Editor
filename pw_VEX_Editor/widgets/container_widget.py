try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
import os, hou, re
import input_widget, numbar_widget
reload(input_widget)
reload(numbar_widget)

# reload(houdini_nodes)



class Container(QWidget):
    errorsSignal = Signal(str)
    noErrorsSignal = Signal()
    helpSignal = Signal(str)
    def __init__(self, text, file=None, parm=None, section=None, parent=None):
        super(Container, self).__init__()#parent)
        self.par = parent
        self.is_backup=False
        # UI
        hbox = QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0,0,0,0)
        # text container
        from .. import vex_settings
        self.settings = vex_settings.EditorSettingsClass()
        self.file, self.parm, self.section = file, parm, section
        self.category = None
        # input widget
        self.edit = input_widget.VEXEditorInputWidget(self)
        self.edit.helpSignal.connect(self.helpSignal.emit)
        self.edit.messageSignal.connect(parent.message)
        self.edit.saveSignal.connect(self.save_current_text)
        # # numbers
        self.lineNum = numbar_widget.lineNumberBarClass(self.edit, self)
        # # add widgets
        hbox.addWidget(self.lineNum)
        hbox.addWidget(self.edit)

        self.edit.verticalScrollBar().valueChanged.connect(lambda :self.lineNum.update())

        if text:
            self.set_text(text)

        self.parm_templates = []

    def set_parm(self, parm):
        self.file, self.parm, self.section = None, parm, None
        self.category = self.parm.node().type().category().name().lower()
        self.read_source_text()

    def set_file(self, path):
        self.file, self.parm, self.section = path, None, None
        self.read_source_text()

    def set_section(self, s):
        self.file, self.parm, self.section = None, None, s
        self.category = self.section.definition().nodeType().category().name().lower()
        self.read_source_text()

    def set_empty(self):
        self.file, self.parm, self.section = None, None, None
        self.par.assign_tab_reference(self)

    def set_text(self, text):
        self.edit.setText(text)

    def tab_index(self):
        for i in range(self.par.count()):
            if self == self.par.widget(i):
                return i
        return -1

    def save_current_text(self):
        text = self.edit.toPlainText()

        # update parameters
        from .. import vex_settings
        if self.settings.get_value('auto_update_parms', vex_settings.default_data['auto_update_parms']):
            if self.parm or self.section:
                if not self.update_parameters():
                    print 'Error update parameters'
                    return

        # save code
        if self.file:
            try:
                with open(hou.expandString(self.file), 'w') as f:
                    f.write(text)
            except:
                self.par.message('Error save to file: %s' % self.file)
                return
            self.par.message('File saved: %s' % self.file)
        elif self.section:
            self.section.setContents(text)
            self.par.message('Source code saved to "%s"' % self.section.name())
        elif self.parm:
            try:
                self.parm.set(text)
                QTimer.singleShot(100, lambda :self.check_errors(self.parm.node()))
                return

            except hou.ObjectWasDeleted:
                # hou.ui.displayMessage('Node Was Deleted!',
                #        buttons=('OK',),
                #        severity=hou.severityType.Error,
                #        default_choice=0,
                #        details_expanded=False)
                return
        else:
            self.define_new_source()

    def check_errors(self, node):
        err = node.errors()
        if err:
            self.par.message('Error code "%s"' % self.parm.name())
            self.errorsSignal.emit(err)
            self.setStyleSheet('QTextEdit{border: 1px solid red}')
            return
        warn = node.warnings()
        if warn:
            self.par.message('Warning "%s"' % self.parm.name())
            self.setStyleSheet('QTextEdit{border: 1px solid #a4740e}')
            return
        self.noErrorsSignal.emit()
        self.setStyleSheet('QWidget{border: none}')
        self.par.message('Source code saved to "%s"' % self.parm.name())

    def read_source_text(self):
        if self.file:
            if os.path.exists(hou.expandString(self.file)):
                text = open(hou.expandString(self.file)).read()
            else:
                hou.ui.displayMessage('File not found', buttons=(('OK',)),
                                  severity=hou.severityType.Error,
                                  default_choice=0,
                                  title='Save VEX Code')
                self.set_empty()
                return
            self.set_text(text)
        elif self.parm:
            try:
                text = self.parm.unexpandedString()
            except:
                try:
                    text = self.parm.expression()
                except:
                    print "CANNOT READ PARAMETER"
                    return
            self.set_text(text)
        elif self.section:
            text = self.section.contents()
            self.set_text(text)
        else:
            pass
        self.save_current_declared_parms()

    def define_new_source(self):
        from .. import houdini_nodes
        r = hou.ui.displayMessage('Where you want to save the code?', buttons=('File','Node parameter', 'HDA Section', 'Cancel'),
                                  severity=hou.severityType.ImportantMessage,
                                  default_choice=3,
                                  title='Save VEX Code')
        text = self.edit.toPlainText()

        if r == 0:
            path = hou.ui.selectFile('', 'Save file', False,hou.fileType.Any, '*.h, *.vfl',chooser_mode=hou.fileChooserMode.Write,)
            if path:
                if os.path.isdir(path):
                    hou.ui.displayMessage('You need to choise file', buttons=(('OK',)),
                                  severity=hou.severityType.Error,
                                  default_choice=0,
                                  title='Save VEX Code')
                    return
                if os.path.exists(path):
                     r = hou.ui.displayMessage('Replace existing file?', buttons=('Yes','Cancel'),
                                  severity=hou.severityType.Warning,
                                  default_choice=1,

                                  title='Save VEX Code')
                     if r == 1:
                         return
                if not os.path.splitext(path)[-1] == '.h':
                    path += '.h'
                with open(path, 'w') as f:
                    f.write(text)
                self.par.assign_tab_reference(self, filepath=path)

            return

        elif r == 1:
            s = hou.selectedNodes()
            if s:
                node = s[0]
            else:
                node=None
            n = hou.ui.selectNode(initial_node=node)
            if n:

                parms = houdini_nodes.get_parms_from_node(hou.node(n))
                # names = {x.name(): x for x in parms} # python 2.7
                names = {}
                for x in parms:
                    names[x.name()] = x
                p = hou.ui.selectFromList(names.keys(),
                                          exclusive=True,
                                          message='Select parameter to save VEX code',
                                          title='Select Parameter')
                if p:
                    parm = names[names.keys()[p[0]]]
                    val = parm.eval()
                    if val:
                        r = hou.ui.displayMessage('Replace existing Value?', buttons=('Yes','Cancel'),
                                  severity=hou.severityType.Warning,
                                  default_choice=1,
                                  title='Save VEX Code')
                        if r == 1:
                            return
                    parm.set(text)
                    self.par.assign_tab_reference(self,  parm=parm)

        elif r == 2:
            s = hou.selectedNodes()
            if s:
                node = s[0]
            else:
                node=None
            n = hou.ui.selectNode(initial_node=node)
            if n:
                sections = houdini_nodes.get_sections_from_node(hou.node(n))
                s = hou.ui.selectFromList(sections.keys(),
                                          exclusive=True,
                                          message='Select parameter to save VEX code',
                                          title='Select Parameter')
                if s:
                    section = sections[sections.keys()[s[0]]]
                    val = section.contents()
                    if val:
                        r = hou.ui.displayMessage('Replace existing Value?', buttons=('Yes','Cancel'),
                                  severity=hou.severityType.Warning,
                                  default_choice=1,
                                  title='Save VEX Code')
                        if r == 1:
                            return
                    section.setContents(text)
                    self.par.assign_tab_reference(self,  section=section)
        else:
            return

    def update_parameters(self):
        # parse text
        declar = self.find_parameters_in_text()
        # for wrangle
        if self.parm:
            try:
                grp = self.parm.node().parmTemplateGroup()
                grp = self.update_parm_template_group(grp, declar)
                self.parm.node().setParmTemplateGroup(grp)
            except hou.ObjectWasDeleted:
                hou.ui.displayMessage('Node Was Deleted!',
                       buttons=('OK',),
                       severity=hou.severityType.Error,
                       default_choice=0,
                       details_expanded=False)
                return
        # for operator
        elif self.section:
            # todo: update parameters on operator UI
            return True
        else:
            return
        # save parameter list
        self.save_current_declared_parms(declar)
        return True

    def update_parm_template_group(self, grp, new_parms):
        # remove deleted parameters
        # names = {x['name']:x for x in new_parms} # python 2.7
        names = {}
        for x in new_parms:
            names[x['name']] = x
        for p in self.parm_templates:
            # not used more
            if not p['name'] in names:
                p = grp.find(p['name'])
                if p:
                    grp.remove(p.name())
            else:
                # type changed
                if not p['func'] == names[p['name']]['func']:
                    p = grp.find(p['name'])
                    if p:
                        grp.remove(p.name())
        # create parms
        from .. import vex_settings
        top = self.settings.get_value('create_parms_on_top',vex_settings.default_data['create_parms_on_top'])
        for parm in new_parms:
            if not grp.find(parm['name']):
                newparm = self.get_new_parameter(parm)
                if newparm:
                    if top:
                        grp.insertBefore(grp.entries()[0], newparm)
                    else:
                        grp.addParmTemplate(newparm)
        return grp

    def save_current_declared_parms(self, parms=None):
        if not parms:
            parms = self.find_parameters_in_text()
        self.parm_templates = parms

    def get_new_parameter(self, parm):
        # ch, chf - float
        # chv - vector
        # chp - point
        # chs - string
        # chi- int
        # chramp - ramp

        if parm['func'] == 'ch' or parm['func'] == 'chf':
            return hou.FloatParmTemplate(parm['name'], parm['name'].title(), 1)

        elif parm['func'] == 'chv':
            return hou.FloatParmTemplate(parm['name'], parm['name'].title(), 3)

        elif parm['func'] == 'chs':
            return hou.StringParmTemplate(parm['name'], parm['name'].title(), 1)

        elif parm['func'] == 'chi':
            return hou.IntParmTemplate(parm['name'], parm['name'].title(), 1)

        elif parm['func'] == 'chramp':
            if parm['type'] == 'vector':
                return hou.RampParmTemplate(parm['name'], parm['name'].title(), hou.rampParmType.Color )
            else:
                return hou.RampParmTemplate(parm['name'], parm['name'].title(), hou.rampParmType.Float )

        elif parm['func'] == 'chp':
            return hou.FloatParmTemplate(parm['name'], parm['name'].title(), 4)

    def find_parameters_in_text(self):
        text = self.edit.toPlainText()
        pat = r'((\w+)\s+\w+\s*=\s*)?(ch[visrampf]*)\s*\([\'"](.+?)[\'"]\)'
        result = []
        for d in re.findall(pat,text):
            if not re.findall(r"[./]", d[-1]):
                result.append(dict(
                    func=d[2].strip(),
                    name=d[3],
                    type=d[1]
                ))
        return  result


