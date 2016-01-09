from PySide.QtCore import *
from PySide.QtGui import *
import json, os, glob, webbrowser
import hou, hqt
from widgets import editor_window_UIs
reload(editor_window_UIs)
from widgets import tab_widget, select_parm_dialog, completer_widget, error_browser
reload(tab_widget)
reload(completer_widget)
reload(select_parm_dialog)
reload(error_browser)
from widgets.vexSyntax import design
reload(design)
import houdini_nodes
reload(houdini_nodes)
from icons.icons import icons
import vex_settings
reload(vex_settings)
import template_editor
reload(template_editor)
import options_dialog
reload(options_dialog)
from autocomplete import vex_parser
import theme_editor
reload(theme_editor)
from . import check_version
reload(check_version)

main = __import__('__main__').__dict__


class VEXEditorPanelClass(QMainWindow, editor_window_UIs.Ui_editor_window):
    def __init__(self):
        super(VEXEditorPanelClass, self).__init__()
        self.setupUi(self)
        ver = check_version.get_current_version()
        self.version = 'v%s.%s.%s' % (ver[0], ver[1], ver[2])
        # settings
        self.settings = vex_settings.EditorSettingsClass()
        self.theme = ''
        self.theme_colors = {}
        self.load_settings()
        self.hstyle = hqt.get_h14_style(self.theme)
        # build ui
        self.errors = error_browser.ErrorBrowserWidget()
        self.error_browser_ly.addWidget(self.errors)
        self.errors.hide()
        self.tab = tab_widget.VEXEditorTabWidget(self)
        self.tab_ly.addWidget(self.tab)
        self.tab.update_infoSignal.connect(self.set_tab_info)
        self.tab.messageSignal.connect(self.show_status_message)
        self.tab.lastClosedSignal.connect(self.last_tab_closed)

        #icons
        for btn in self.load_from_file_btn, self.load_from_selected_extra_btn, self.save_current_btn, self.reload_current_btn,\
                self.blank_tab_btn, self.load_from_selected_btn:
            btn.setIconSize(QSize(30,30))
        self.load_from_file_btn.setText('')
        self.load_from_file_btn.setIcon(QIcon(icons['header']))

        self.load_from_selected_extra_btn.setText('')
        self.load_from_selected_extra_btn.setIcon(QIcon(icons['vopnode_list']))

        self.load_from_selected_btn.setText('')
        self.load_from_selected_btn.setIcon(QIcon(icons['wrangle']))


        self.save_current_btn.setText('')
        self.save_current_btn.setIcon(QIcon(icons['save']))

        self.reload_current_btn.setText('')
        self.reload_current_btn.setIcon(QIcon(icons['reload_sourse']))

        self.blank_tab_btn.setText('')
        self.blank_tab_btn.setIcon(QIcon(icons['blank']))

        # connects
        self.load_from_selected_extra_btn.clicked.connect(self.create_parm_tab)
        self.load_from_selected_btn.clicked.connect(lambda :self.create_parm_tab(True))
        self.create_from_node_act.triggered.connect(self.create_parm_tab)
        self.load_from_file_btn.clicked.connect(self.create_file_tab)
        self.create_from_file_act.triggered.connect(self.create_file_tab)
        self.reload_current_btn.clicked.connect(self.tab.reload_source)
        self.reload_source_act.triggered.connect(self.tab.reload_source)
        self.save_current_btn.clicked.connect(self.tab.save_current)
        self.save_to_new_act.triggered.connect(self.tab.save_as_current)
        self.save_section_act.triggered.connect(self.tab.save_current)
        self.show_sourse_btn.clicked.connect(self.tab.select_tab_node)
        self.show_sourse_btn_2.clicked.connect(self.tab.open_tab_file)
        self.blank_tab_btn.clicked.connect(self.create_empty_tab)
        self.create_empty_act.triggered.connect(self.create_empty_tab)
        self.context_help_act.triggered.connect(self.tab.show_context_help)
        self.vex_manual_act.triggered.connect(self.tab.open_VEX_manual)
        self.manual_act.triggered.connect(lambda :self.open_url(vex_settings.help_url))
        self.about_act.triggered.connect(self.show_about)
        # self.save_tabs_in_hip_act.triggered.connect(self.tab.save_tabs_to_hip)
        self.load_tabs_from_hip_act.triggered.connect(self.tab.restore_tabs_from_hip)
        self.clear_tabs_act.triggered.connect(self.tab.clear_tabs_node)
        self.check_new_version_act.triggered.connect(check_version.check_version)
        for act in self.auto_create_parms_act, self.save_tabs_in_hip_act, self.use_hou_browser_act:
            act.triggered.connect(self.save_settings)
        # self.set_font_size_act.triggered.connect(self.set_font_size)
        self.live_template_editor_act.triggered.connect(self.open_live_template_editor)
        self.options_act.triggered.connect(self.open_options_dialog)
        self.menu_tabs.aboutToShow.connect(self.update_backup_menu)
        self.open_backup_folder_act.triggered.connect(lambda :webbrowser.open(vex_settings.backup_folder()))
        self.clear_backups_act.triggered.connect(self.clear_backup)
        self.open_theme_editor_act.triggered.connect(self.open_theme_editor)
        self.open_settings_folder_act.triggered.connect(self.open_settings_folder)

        # default visibility
        self.file_info_wd.setVisible(0)
        self.node_info_wd.setVisible(0)
        self.reload_current_btn.setEnabled(0)
        self.save_current_btn.setEnabled(0)

        # temp ui state
        # menu
        self.theme_menu()
        # save main widget to main namespace
        main['vexeditor'] = self

        # start
        self.check_tabs_exists()
        self.update_templates_menu()
        QTimer.singleShot( 50,lambda :self.set_theme(self.theme))
        vex_parser.generate()

    def closeEvent(self, event):
        self.save_settings()
        if self.settings.get_value('auto_save_tabs', vex_settings.default_data['auto_save_tabs']):
            self.tab.save_tabs_to_hip()
        self.tab.timer.stop()
        QMainWindow.closeEvent(self, event)

    def load_settings(self):
        data = self.settings.get_settings()
        self.theme = data.get('theme', self.theme or vex_settings.default_data['theme'])
        self.toolbar_wd.setVisible(data.get('show_toolbar', True))

    def save_settings(self, *args):
        data = self.settings.get_settings()
        data['theme'] = self.theme
        # save data
        self.settings.save_settings(data)


    def set_tab_info(self, data):
        if data['mode'] == 0:
            self.file_info_wd.setVisible(0)
            self.node_info_wd.setVisible(0)
            self.empty_wd.setVisible(1)
        elif data['mode'] == 1: #parm
            self.empty_wd.setVisible(0)
            self.file_info_wd.setVisible(0)
            self.node_info_wd.setVisible(1)
            self.show_sourse_btn.setVisible(1)
            self.empty_wd.setVisible(0)
            self.node_info_lb.setText(data['text'])
        elif data['mode'] == 2: #section
            self.file_info_wd.setVisible(0)
            self.node_info_wd.setVisible(1)
            self.show_sourse_btn.setVisible(0)
            self.empty_wd.setVisible(0)
            self.node_info_lb.setText(data['text'])
        elif data['mode'] == 3: #file
            self.file_info_wd.setVisible(1)
            self.node_info_wd.setVisible(0)
            self.empty_wd.setVisible(0)
            self.file_info_lb.setText(data['text'])
        else:
            self.file_info_wd.setVisible(0)
            self.node_info_wd.setVisible(0)
            self.empty_wd.setVisible(1)
        self.check_tabs_exists()

    def check_tabs_exists(self):
        if self.tab.count():
            self.reload_current_btn.setEnabled(1)
            self.save_current_btn.setEnabled(1)
            self.reload_source_act.setEnabled(1)
            self.save_section_act.setEnabled(1)
            self.save_to_new_act.setEnabled(1)
        else:
            self.reload_current_btn.setEnabled(0)
            self.save_current_btn.setEnabled(0)
            self.reload_source_act.setEnabled(0)
            self.save_section_act.setEnabled(0)
            self.save_to_new_act.setEnabled(0)

    def create_parm_tab(self, fast=False):
        # get node
        node = houdini_nodes.get_selected_node()
        if not node:
            hou.ui.displayMessage('Select Node Before', buttons=(('OK',)),
                                  severity=hou.severityType.Warning,
                                  default_choice=0,
                                  title='Read VEX Code')
            return
        # chose parm \ section
        prms = houdini_nodes.get_parms_from_node(node)
        # parms = {x.name():x for x in parms}
        parms = {}
        for x in prms:
            parms[x.name()] = x
        # sections = nodes.get_sections_from_node(node)
        # sections = {sections[x].name():sections[x] for x in sections}

        sctns = houdini_nodes.get_sections_from_node(node)
        sections = {}
        for x in sctns:
            sections[sctns[x].name()] = sctns[x]

        if fast:
            attr_exists = False
            parm = {'parm':None,
                    'section':None}
            for p in parms:
                if p in select_parm_dialog.fast_open_list:
                    parm['parm'] = p
                    attr_exists = True
                    break
            if not parm['parm']:
                for s in sections:
                    if s in select_parm_dialog.fast_open_list:
                        parm['section'] = s
                        attr_exists = True
                        break
            if not attr_exists:
                self.create_parm_tab(False)
        else:
            parm = self.select_parm_dialog(parms, sections, node)

        # create new tab
        if parm:
            if parm['parm']:
                # check exists parm tab
                parm = parms[parm['parm']]
                exists = self.tab.check_exists_tab(parm=parm)
                if not exists is None:
                    self.show_status_message('Parameter allready opened')
                    self.tab.setCurrentIndex(exists)
                else:
                    t = self.tab.add_tab()
                    self.tab.assign_tab_reference(t, parm=parm)
                    # add rename callback

            elif parm['section']:
                section = sections[parm['section']]
                exists = self.tab.check_exists_tab(section=section)
                if not exists is None:
                    self.show_status_message('Section allready opened')
                    self.tab.setCurrentIndex(exists)
                else:
                    t = self.tab.add_tab()
                    self.tab.assign_tab_reference(t, section=section)
        self.check_tabs_exists()

    def select_parm_dialog(self, parms, sections, node):
        dial = select_parm_dialog.SelectParameterDialogClass(parms, sections, node, self)
        dial.setStyleSheet(self.hstyle)
        if dial.exec_():
            data = dial.get_data()
            if data:
                return data

    def create_file_tab(self):
        # get file
        path = hou.ui.selectFile('', 'Select .h or .vfl file', False,hou.fileType.Any, '*.h, *.vfl')
        if path:
            # check file exists in tabs
            exists = self.tab.check_exists_tab(filepath=path)
            if not exists is None:
                self.show_status_message('File allready opened')
                self.tab.setCurrentIndex(exists)
            else:
                # create new tab
                t = self.tab.add_tab()
                # set file
                self.tab.assign_tab_reference(t, filepath=path)
                self.reload_current_btn.setEnabled(1)
                self.save_current_btn.setEnabled(1)

    def create_empty_tab(self):
        self.tab.add_tab()
        self.reload_current_btn.setEnabled(1)
        self.save_current_btn.setEnabled(1)

    def show_status_message(self, text):
        self.statusBar().showMessage(text, 3000)

    def last_tab_closed(self):
        self.reload_current_btn.setEnabled(0)
        self.save_current_btn.setEnabled(0)

    def show_about(self):
        dial = QDialog(hqt.getHouWindow())
        dial.setWindowTitle('VEX Editor ' + self.version)
        ly = QVBoxLayout()
        dial.setLayout(ly)
        label = QLabel()
        label.setText('''<h2>Houdini VEX Editor {version}</h2>
<p>by PaulWinex. 2015</p>'''.format(version=self.version))
        label.setAlignment(Qt.AlignHCenter)
        ly.addWidget(label)
        imglabel = QLabel()
        i = icons.get('pw_logo')
        if i:
            img = QPixmap(i)
            imglabel.setPixmap(img)
            imglabel.setAlignment(Qt.AlignHCenter)
            ly.addWidget(imglabel)
        btn = QPushButton('www.paulwinex.ru')
        btn.setFlat(True)
        ly.addWidget(btn)
        btn.clicked.connect(lambda :self.open_url(vex_settings.help_url))
        dial.setStyleSheet(self.hstyle)
        dial.exec_()

    def open_url(self, url):
        import webbrowser
        webbrowser.open(vex_settings.help_url)


    def theme_menu(self):
        actions = self.menuTheme.actions()
        for i in actions[2:]:
            self.menuTheme.removeAction(i)

        path = os.path.join(os.path.dirname(__file__), 'colors').replace('\\','/')
        files = glob.glob1(path, '*.json')
        for f in files:
            full = os.path.join(path, f).replace('\\','/')
            d = json.load(open(full))
            a = QAction(d['name'], self, triggered=lambda f=d['name']:self.set_theme(f))
            self.menuTheme.addAction(a)

    def set_theme(self, theme=None):
        theme = theme or self.theme
        themes = design.get_themes()
        if theme in themes:
            theme = themes[theme]
        else:
            theme = design.defaultColors
        # ui theme
        self.hstyle = hqt.get_h14_style(theme['houdini_theme'])
        self.setStyleSheet(self.hstyle)
        # editor theme
        for i in range(self.tab.count()):
            w = self.tab.widget(i).edit
            w.apply_style(theme['name'], theme)
        self.theme = theme['name']
        self.theme_colors = theme
        self.save_settings()
        # update numbar widgets
        self.tab.update_numbars()

    def open_live_template_editor(self):
        self.te = template_editor.TemplateEditorClass(hqt.houWindow, self.theme)
        self.te.setStyleSheet(self.styleSheet())
        self.te.exec_()
        self.tab.update_templates()
        self.update_templates_menu()

    def update_templates_menu(self):
        actions = self.menuTemplates.actions()
        for i in actions[2:]:
            self.menuTemplates.removeAction(i)
        templates = template_editor.TemplateEditorClass.get_templates()
        for t in templates:
            act = QAction(t['name'], self.menuTemplates)
            act.triggered.connect(lambda t=t:self.tab.insert_to_current(t['text']))
            self.menuTemplates.addAction(act)

    def update_backup_menu(self):
        actions = self.backup_menu_act.actions()
        for i in actions[3:]:
            self.backup_menu_act.removeAction(i)

        backupdir = vex_settings.backup_folder()
        for b in glob.glob1(backupdir, '*.backup'):
            act = QAction(b, self)
            # act.setData(os.path.join(backupdir, b).replace('\\','/'))
            path = os.path.join(backupdir, b).replace('\\','/')
            act.triggered.connect(lambda x=path: self.restore_backup(x))
            self.backup_menu_act.addAction(act)

    def restore_backup(self, path):
        tab = self.tab.add_tab()
        self.tab.assign_tab_reference(tab, backup=path)

    def clear_backup(self):
        folder = vex_settings.backup_folder()
        for f in os.listdir(folder):
            try:
                os.remove(os.path.join(folder, f))
            except:
                pass


    def open_options_dialog(self):
        self.dial = options_dialog.OptionsDialogClass(hqt.houWindow)
        self.dial.setStyleSheet(self.hstyle)
        def update_from_settings():
            s = self.settings.get_settings()
            self.toolbar_wd.setVisible(s.get('show_toolbar', True))
        self.dial.optionsChangedSignal.connect(self.tab.update_from_settings)
        self.dial.optionsChangedSignal.connect(update_from_settings)
        self.dial.exec_()

    def open_theme_editor(self):
        self.themeedit = theme_editor.ThemeEditorClass(hqt.houWindow)
        self.themeedit.themesUpdatedSignal.connect(self.theme_menu)
        self.themeedit.show()

    def open_settings_folder(self):
        d = self.settings.settings_dir()
        if os.path.exists(d):
            self.open_folder(d)
        else:
            print 'Error path %s ' % d

    def open_folder(self, path):
        if os.name == 'nt':
            os.startfile(path)
        elif os.name == 'posix':
            os.system('xdg-open "%s"' % path.replace('\\','/'))
        elif os.name == 'os2':
            os.system('open "%s"' % path.replace('\\','/'))
        else:
            print os.name



    ###########################################################################
    ###########################################################################
    ###########################################################################

    ########################### DROP
    def dragEnterEvent(self, event):
        event.acceptProposedAction()
        QMainWindow.dragEnterEvent(self,event)
    def dragMoveEvent(self, event):
        event.acceptProposedAction()
        QMainWindow.dragMoveEvent(self,event)
    def dragLeaveEvent(self, event):
        event.accept()
        QMainWindow.dragLeaveEvent(self,event)
    def dropEvent(self, event):
        event.acceptProposedAction()
        event.accept()
        if  event.mimeData().hasText():
            mim = event.mimeData()
            text = mim.text()
            p = hou.parm(text)
            if p:
                if type(p) == hou.Parm:
                    if p.parmTemplate().type() == hou.parmTemplateType.String:
                        exists = self.tab.check_exists_tab(parm=p)
                        if not exists is None:
                            self.show_status_message('Parameter allready opened')
                            self.tab.setCurrentIndex(exists)
                        else:
                            t = self.tab.add_tab()
                            self.tab.assign_tab_reference(t, parm=p)
        QMainWindow.dropEvent(self,event)