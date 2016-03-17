import editor_panel


def show(*args, **kwargs):
    import hqt
    reload(hqt)
    reload(editor_panel)
    hqt.show(editor_panel.VEXEditorPanelClass, name='VEX Editor',replacePyPanel=0, hideTitleMenu=0)


import vex_settings