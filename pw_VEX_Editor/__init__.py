import editor_panel
reload(editor_panel)

def show(*args, **kwargs):
    import hqt
    reload(hqt)
    hqt.show(editor_panel.VEXEditorPanelClass, name='VEX Editor',replacePyPanel=0, hideTitleMenu=0)


import vex_settings