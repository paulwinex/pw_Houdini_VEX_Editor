from PySide.QtCore import *
from PySide.QtGui import *
import hqt, hou, datetime, time, os
from .. autocomplete import keywords
reload(keywords)
import context_help
reload(context_help)
import container_widget
reload(container_widget)
from .. import vex_settings
tabsNodeName = 'VexEditorTabs'

class VEXEditorTabWidget(QTabWidget):
    update_infoSignal = Signal(dict)
    messageSignal = Signal(str)
    lastClosedSignal = Signal()
    def __init__(self, parent):
        super(VEXEditorTabWidget, self).__init__(parent)
        # ui
        self.setTabsClosable(True)
        self.setMovable(True)
        # variables
        self.par = parent
        self.settings = vex_settings.EditorSettingsClass()
        # connect
        self.tabCloseRequested.connect(self.closeTab)
        self.currentChanged.connect(self.update_info)
        # backup timer
        self.timer = QTimer()
        self.timer.setInterval(self.settings.get_value('backup_timeout', vex_settings.default_data['backup_timeout']) * 60000)
        self.timer.timeout.connect(self.create_backup)
        # start
        self.restore_tabs_from_hip()
        self.update_backup_timer()

    def closeTab(self, i):
        if QMessageBox.question(hqt.houWindow, 'Close Tab',
                               'Close this tab without saving?\n'+self.tabText(i),
                               QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            self.removeTab(i)
        if self.count()== 0:
            self.lastClosedSignal.emit()
            self.update_info()

    def add_tab(self, **kwargs):
        con = container_widget.Container('', parent=self)
        con.errorsSignal.connect(self.par.errors.show_error)
        con.noErrorsSignal.connect(self.par.errors.clear)
        self.addTab(con, 'Vex Code')
        self.assign_tab_reference(con, **kwargs)
        self.setCurrentIndex(self.count()-1)
        con.edit.apply_style(self.par.theme_colors.get('name',''), self.par.theme_colors)
        return con

    def assign_tab_reference(self, tab,  parm=None, section=None, filepath=None, backup=None):
        if not any([parm,section, filepath, backup]):
            title = 'VEX Code'
            self.setTabText(tab.tab_index(), title)
            self.update_info()
            return
        if filepath and not all([parm, section]):
            title = os.path.basename(filepath)
            tab.set_file(filepath)
            self.setTabText(tab.tab_index(), title)
            self.update_info()
            return
        elif backup:
            title = os.path.basename('Backup file')
            tab.set_file(backup)
            tab.is_backup = True
            self.setTabText(tab.tab_index(), title)
            self.update_info()
            return
        elif parm and not all([filepath, section]):
            title = '%s | %s' % (parm.node().path(), parm.name())
            tab.set_parm(parm)
            self.setTabText(tab.tab_index(), title)
            try:
                parm.node().removeEventCallback((hou.nodeEventType.NameChanged,) , self.update_info)
            except:
                pass
            parm.node().addEventCallback((hou.nodeEventType.NameChanged,) , self.update_info)
            self.update_info()
            return
        elif section and not all([filepath, parm]):
            title = '%s | %s' % (section.definition().nodeTypeName(), section.name())
            tab.set_section(section)
            self.setTabText(tab.tab_index(), title)
            self.update_info()
            return
        print 'Error data to assign'

    def message(self, *args):
        self.messageSignal.emit(' '.join(args))

    def reload_source(self):
        cur = self.current()
        if cur:
            cur.read_source_text()
        self.update_numbars()

    def save_current(self):
        c = self.current()
        if c:
            c.save_current_text()

    def save_as_current(self):
        c = self.current()
        if c:
            c.define_new_source()

    def create_backup(self):
        self.messageSignal.emit('Backup...')
        widgets = []
        for i in range(self.count()):
            w = self.widget(i)
            if w.is_backup:
                continue
            text = w.edit.text()
            if not text:
                continue
            if w.file:
                parm_path = os.path.basename(w.file)
            elif w.parm:
                parm_path = (w.parm.node().path() + '/' + w.parm.name()).replace('/','_')
            elif w.section:
                parm_path = (w.section.definition().nodeTypeName()+'_'+w.section.name())
            else:
                parm_path = 'empty_tab'
            widgets.append([text, parm_path])

        class Backuper(QObject):
            finished = Signal()
            def __init__(self, widgets):
                super(Backuper, self).__init__()
                self.widgets = widgets
                self.save_dir = vex_settings.backup_folder()

            def save(self):
                self.clear_old_files()
                t = datetime.datetime.now()
                stamp='{year}-{month}-{day}_{hour}h-{min}m-{sec}s'.format(
                                                    year=t.year,
                                                    month=t.month,
                                                    day=t.day,
                                                    hour=t.hour,
                                                    min=t.minute,
                                                    sec=t.second)
                if not os.path.exists(self.save_dir):
                    try:
                        os.makedirs(self.save_dir)
                    except:
                        print 'Error create backup folder', self.save_dir
                        return
                for w in self.widgets:
                    filename = os.path.join(self.save_dir, '%s(%s)_%s.backup' % (hou.hipFile.basename(), w[1], stamp)).replace('\\','/')
                    with open(filename, 'w') as f:
                        f.write(w[0])
                    time.sleep(0.1)

            def clear_old_files(self):
                max_files =  max(3, vex_settings.default_data['max_backup_files'] - len(self.widgets))
                if os.path.exists(self.save_dir) and os.path.isdir(self.save_dir):
                    if len(os.listdir(self.save_dir)) > max_files:
                        files = list(sorted([os.path.join(self.save_dir, x).replace('\\','/') for x in os.listdir(self.save_dir)],
                                            key=lambda f: os.path.getmtime(os.path.join(self.save_dir, f))))
                        files.reverse()
                        for f in files[max_files:]:
                            try:
                                os.remove(f)
                            except:
                                pass

        self.thread = QThread(self)
        self.w = Backuper(widgets)
        self.w.moveToThread(self.thread)
        self.thread.started.connect(self.w.save)
        self.w.finished.connect(self.thread.quit)
        self.thread.start()

    def current(self):
        i = self.currentIndex()
        w = self.widget(i)
        return w

    def update_info(self, **kwargs):
        cur = self.current()
        if not cur:
            self.update_infoSignal.emit(dict(
                mode=0,
                text=''
            ))
            return
        if cur.parm:
            self.update_infoSignal.emit(dict(
                mode=1,
                text='Node: %s\nParm: %s' % (cur.parm.node().path(), cur.parm.name())
            ))
            title = '%s | %s' % (cur.parm.node().path(), cur.parm.name())
            self.setTabText(cur.tab_index(), title)
        elif cur.section:
            self.update_infoSignal.emit(dict(
                mode=2,
                text='Node Type: %s\nSection: %s' % (cur.section.definition().nodeTypeName(), cur.section.name())
            ))
        elif cur.file:
            self.update_infoSignal.emit(dict(
                mode=3,
                text = cur.file
            ))
        else:
            self.update_infoSignal.emit(dict(
                mode=0,
                text=''
            ))

    def select_tab_node(self):
        c = self.current()
        if c.parm:
            c.parm.node().setCurrent(1)

    def open_tab_file(self):
        c = self.current()
        if c.file:
            self.par.open_folder(os.path.dirname(hou.expandString(c.file)))


#######################################################################

    def get_help_url(self):
        if self.settings.get_value('use_online_manual', False):
            return vex_settings.help_online_url
        else:
            return vex_settings.help_local_url

    def open_VEX_manual(self):
        url = self.get_help_url()+'vex/'
        self.open_url_in_help_browser(url)

    def show_context_help(self):
        cur = self.current()
        tc = cur.edit.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        text = tc.selectedText()
        if not text:
            return

        # special link
        for h in context_help.context_help:
            if text in h['names']:
                self.open_url_in_help_browser(self.get_help_url()+h['link'])
                return

        # if function
        if text in keywords.words['functions_all']:
            url = self.get_help_url()+'vex/functions/'
        else:
            url = self.get_help_url()+'find?q='
        self.open_url_in_help_browser(url+text)

    def open_url_in_help_browser(self, url):
        if self.settings.get_value('use_external_browser', False):
            import webbrowser
            webbrowser.open_new(url)
        else:
            desktop = hou.ui.curDesktop()
            browser = desktop.paneTabOfType(hou.paneTabType.HelpBrowser)
            if browser is None:
                browser = desktop.createFloatingPane(hou.paneTabType.HelpBrowser)
            browser.setUrl(url)
        QTimer.singleShot(200, self.focus_me)

    def focus_me(self):
        cur = self.current()
        if cur:
            cur.edit.setFocus()
            cur.edit.activateWindow()

    def save_tabs_to_hip(self):
        # collect data
        tabs = []
        for i in range(self.count()):
            c = self.widget(i)
            if c.is_backup:
                continue
            text = c.edit.text()
            if c.parm:
                type = 'parm'
                path = c.parm.path()
            elif c.file:
                type = 'file'
                path = c.file
            elif c.section:
                type = 'section'
                path = '/'.join([c.section.definition().nodeType().name(), c.section.name()])
            else:
                type = 'empty'
                path=''
            tabs.append(dict(
                text=text,
                type=type,
                path=path
            )
            )
        if not tabs:
            return

        # create node
        self.clear_tabs_node()
        node = hou.node('/obj').createNode('vopnet')
        node.setName(tabsNodeName)

        # create template
        grp = node.parmTemplateGroup()

        for i, tab in enumerate(tabs):
            tp = hou.StringParmTemplate('type%s' % i, 'type%s' % i, 1, (tab['type'],))
            path = hou.StringParmTemplate('path%s' % i, 'path%s' % i, 1, (tab['path'],))
            text = hou.StringParmTemplate('text%s' % i, 'text%s' % i, 1, (tab['text'],))
            text.setTags({"editor": "1"})
            name = os.path.basename(tab['path'])
            if not name:
                name = 'VEX Code%s' % i
            f = hou.FolderParmTemplate(name, name.replace('.','_').lower(), (tp, path, text))
            grp.addParmTemplate(f)

        ind = hou.IntParmTemplate('tabs_active_index', 'tabs_active_index', 1, (self.currentIndex(),))
        grp.addParmTemplate(ind)

        node.setParmTemplateGroup(grp)
        node.hide(True)

    def restore_tabs_from_hip(self):
        node = hou.node('obj/'+tabsNodeName)
        if not node:
            self.messageSignal.emit('Saved tabs not found')
            return
        ptg = node.parmTemplateGroup()
        tabs = []
        for i in range(len(ptg.entries())):
            type = node.parm('type%s' % i)
            path = node.parm('path%s' % i)
            text = node.parm('text%s' % i)
            if all([type, path, text]):
                tabs.append(dict(
                    type=type.eval(),
                    path=path.eval(),
                    text=text.eval()
                ))
        if tabs:
            errors = []
            for tab in tabs:
                if tab['type'] == 'parm':
                    parm = hou.parm(tab['path'])
                    if parm:
                        t = self.add_tab()
                        self.assign_tab_reference(t, parm=parm)
                        t.edit.setText(tab['text'])
                    else:
                        t = self.add_tab()
                        t.edit.setText(('!!! ERROR\n!!! PARAMETER NOT FOUND: %s\n\n' % tab['path']) + tab['text'])
                        errors.append(tab)

                elif tab['type'] == 'section':
                    name, sect = tab['path'].split('/')
                    definition = self.get_definition(name)
                    if definition:
                        if sect in definition.sections().keys():
                            section = definition.sections()[sect]
                            t = self.add_tab()
                            self.assign_tab_reference(t, section=section)
                            t.edit.setText(tab['text'])
                            continue
                    t = self.add_tab()
                    t.edit.setText(('!!! ERROR\n!!! SECTION OR DEFINITION NOT FOUND: %s\n\n' % tab['path']) + tab['text'])
                    errors.append(tab)

                elif tab['type'] == 'file':
                    if os.path.exists(tab['path']):
                        t = self.add_tab()
                        self.assign_tab_reference(t, filepath=tab['path'])
                        t.edit.setText(tab['text'])
                    else:
                        t = self.add_tab()
                        t.edit.setText(('!!! ERROR\n!!! FILE NOT FOUND: %s\n\n' % tab['path']) + tab['text'])
                        errors.append(tab)
                elif tab['type'] == 'empty':
                    t = self.add_tab()
                    t.edit.setText(tab['text'])
        ind_parm = node.parm('tabs_active_index')
        if ind_parm:
            i = ind_parm.eval()
            if i < self.count():
                self.setCurrentIndex(i)

        QTimer.singleShot(100,self.update_info)

    def clear_tabs_node(self):
        node = hou.node('obj/'+tabsNodeName)
        if node:
            node.destroy()

    def get_definition(self, name):
        for key in hou.nodeTypeCategories().keys():
            for k in hou.nodeTypeCategories()[key].nodeTypes().keys():
                if name == k:
                    return hou.nodeTypeCategories()[key].nodeTypes()[k].definition()

    def check_exists_tab(self, parm=None, filepath=None, section=None):
        if parm:
            for i in range(self.count()):
                w = self.widget(i)
                if w.parm == parm:
                    return i
        elif filepath:
            for i in range(self.count()):
                w = self.widget(i)
                if w.file == filepath:
                    return i
        elif section:
            for i in range(self.count()):
                w = self.widget(i)
                if w.section == section:
                    return i

    def update_numbars(self):
        for i in range(self.count()):
            self.widget(i).lineNum.update()

    def update_templates(self):
        for i in range(self.count()):
            self.widget(i).edit.update_live_templates()

    def insert_to_current(self, text):
        cur = self.current()
        if cur:
            cursor = cur.edit.textCursor()
            pos = cursor.position()
            cursor.insertText(text.replace('$cursor$',''))
            offs = max(text.find('$cursor$'),0)
            cursor.setPosition(pos+offs)
            cur.edit.setTextCursor(cursor)
            QTimer.singleShot(100, self.focus_me)

    def update_from_settings(self):
        for i in range(self.count()):
            self.widget(i).edit.update_from_settings()
            self.widget(i).lineNum.update()
        self.update_backup_timer()

    def update_backup_timer(self):
        if self.settings.get_value('create_backups', vex_settings.default_data['create_backups']):
            self.timer.start()
        else:
            self.timer.stop()
