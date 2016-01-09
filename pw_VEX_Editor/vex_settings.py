import os, json, hou, hqt

settings_file_name = 'settings.json'
help_url = 'http://www.paulwinex.ru/vex_editor_1_0_5/'

help_local_url = 'http://127.0.0.1:48626/'
help_online_url = 'http://www.sidefx.com/docs/houdini%s/' % '.'.join([str(x) for x in hou.applicationVersion()[:2]])

houdini_themes = {
    'Houdini Dark':'Dark',
    'Houdini Light':'Light',
    'Houdini Pro':'Pro'
}

current_theme = houdini_themes.get(hqt.getCurrentColorTheme(),"Dark")

default_data = dict(
            font_size=20,
            font_size_min=8,
            font_size_max=60,
            theme=current_theme,
            font_name='Lucida Console',
            auto_update_parms=True,
            create_parms_on_top=False,
            auto_save_tabs=True,
            create_backups=True,
            show_whitespaces=False,
            show_toolbar=True,
            use_online_manual=False,
            use_external_browser=False,
            backup_timeout=3, #min
            max_backup_files=30,
            autocompleter=True
        )

def get_settings_folder():
    path = os.path.join(os.environ.get('HOUDINI_USER_PREF_DIR', os.path.expanduser('~')),'pw_vex_editor')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def backup_folder():
    return os.path.join(get_settings_folder(), '_backups').replace('\\','/')

def get_autocomplete_cache_file():
    return os.path.join(get_settings_folder(), 'autocompleter.json').replace('\\','/')


class EditorSettingsClass(object):
    def __init__(self):
        super(EditorSettingsClass, self).__init__()
        self.path = self.get_file()


    def settings_dir(self):
        return os.path.dirname(self.path)

    def get_file(self):
        path = os.path.join(get_settings_folder(), settings_file_name).replace('\\','/')
        if os.path.exists(path):
            try:
                json.load(open(path))
                return path
            except:
                print 'VEX Editor: ERROR READ SETTINGS FILE'
                try:
                    json.dump({},open(path, 'w'))
                    print 'VEX Editor: NEW FILE CREATED'
                    return path
                except:
                    print 'VEX Editor: ERROR CREATE SETTINGS FILE'
                    return
        else:
            try:
                open(path, 'w').close()
                return path
            except:
                print 'VEX Editor: ERROR CREATE SETTINGS FILE'
                return

    def get_settings(self):
        if self.path:
            try:
                return json.load(open(self.path))
            except:
                return {}
        return {}

    def save_settings(self, data):
        if self.path:
            try:
                json.dump(data, open(self.path, 'w'), indent=4)
                return True
            except:
                print 'VEX Editor: ERROR SAVE SETTINGS FILE'
        return False

    def get_value(self, key, default=None):
        # if default is None:
        #     default = default_data.get(key, None)
        if self.path:
            data = self.get_settings()
            return data.get(key, default)

    def set_value(self, key, value):
        if self.path:
            data = self.get_settings()
            if data:
                data[key] = value
                self.save_settings(data)
                return True


