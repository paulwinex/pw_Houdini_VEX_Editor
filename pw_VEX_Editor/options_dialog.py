from PySide.QtCore import *
from PySide.QtGui import *
from widgets import options_dialog_UIs
reload(options_dialog_UIs)
import vex_settings


class OptionsDialogClass(QDialog, options_dialog_UIs.Ui_Dialog):
    optionsChangedSignal = Signal()
    def __init__(self, parent=None):
        super(OptionsDialogClass, self).__init__(parent)
        self.setupUi(self)
        # connects
        self.save_btn.clicked.connect(self.save_settings)
        self.font_size_spb.valueChanged.connect(self.update_font_preview)
        self.font_name_cbb.currentFontChanged.connect(self.update_font_preview)

        # temp ui state
        # self.create_backup_cbx.setEnabled(0)

        # start
        self.load_settings()

    def save_settings(self):
        """
        Store settings from UI
        """
        s = vex_settings.EditorSettingsClass()
        data = s.get_settings()
        data.update(self.get_ui_data())
        s.save_settings(data)
        self.optionsChangedSignal.emit()
        self.accept()


    def load_settings(self):
        """
        Load settings to init UI
        """
        s = vex_settings.EditorSettingsClass()
        data = s.get_settings()

        # ui config
        self.font_size_spb.setMaximum(data.get('font_size_min',vex_settings.default_data['font_size_min']))
        self.font_size_spb.setMaximum(data.get('font_size_max',vex_settings.default_data['font_size_max']))
        self.font_size_sld.setMaximum(data.get('font_size_min',vex_settings.default_data['font_size_min']))
        self.font_size_sld.setMaximum(data.get('font_size_max',vex_settings.default_data['font_size_max']))
        # parms
        self.font_size_spb.setValue(data.get('font_size',vex_settings.default_data['font_size']))
        self.font_name_cbb.setCurrentFont(QFont(data.get('font_name',vex_settings.default_data['font_name'])))
        self.auto_update_parameters_cbx.setChecked(data.get('auto_update_parms',vex_settings.default_data['auto_update_parms']))
        self.create_parms_on_top.setChecked(data.get('create_parms_on_top',vex_settings.default_data['create_parms_on_top']))
        self.auto_save_tabs_cbx.setChecked(data.get('auto_save_tabs',vex_settings.default_data['auto_save_tabs']))
        self.create_backup_cbx.setChecked(data.get('create_backups',vex_settings.default_data['create_backups']))
        self.show_whitespaces_cbx.setChecked(data.get('show_whitespaces',vex_settings.default_data['show_whitespaces']))
        self.show_toolbar_cbx.setChecked(data.get('show_toolbar',vex_settings.default_data['show_toolbar']))
        self.use_online_manual_cbx.setChecked(data.get('use_online_manual',vex_settings.default_data['use_online_manual']))
        self.use_external_browser_cbx.setChecked(data.get('use_external_browser',vex_settings.default_data['use_external_browser']))
        self.aurocompleter_cbx.setChecked(data.get('autocompleter',vex_settings.default_data['autocompleter']))
        self.help_window_cbx.setChecked(data.get('helpwindow',vex_settings.default_data['helpwindow']))
        # preview
        self.update_font_preview()

    def update_font_preview(self):
        st = '''QLabel{
        font-size:%spx;
        font-family:%s
        }
        ''' % (self.font_size_spb.value(), self.font_name_cbb.currentFont().family())
        self.font_preview_lb.setStyleSheet(st)

    def get_ui_data(self):
        data = dict(
            font_size=self.font_size_spb.value(),
            font_size_min=8,
            font_size_max=60,
            font_name=self.font_name_cbb.currentFont().family(),
            auto_update_parms=self.auto_update_parameters_cbx.isChecked(),
            create_parms_on_top=self.create_parms_on_top.isChecked(),
            auto_save_tabs=self.auto_save_tabs_cbx.isChecked(),
            create_backups=self.create_backup_cbx.isChecked(),
            show_whitespaces=self.show_whitespaces_cbx.isChecked(),
            show_toolbar=self.show_toolbar_cbx.isChecked(),
            use_online_manual=self.use_online_manual_cbx.isChecked(),
            use_external_browser=self.use_external_browser_cbx.isChecked(),
            autocompleter=self.aurocompleter_cbx.isChecked(),
            helpwindow=self.help_window_cbx.isChecked()
        )
        return data


if __name__ == '__main__':
    app = QApplication([])
    w = OptionsDialogClass()
    w.show()
    app.exec_()