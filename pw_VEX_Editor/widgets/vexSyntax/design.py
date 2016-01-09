# import settingsManager
import os, re, json, hqt

houdini_themes = {
    'Houdini Dark':'Dark',
    'Houdini Light':'Light',
    'Houdini Pro':'Pro'
}

current_theme = houdini_themes.get(hqt.getCurrentColorTheme(),"Dark")


# EditorStyle = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'style', 'completer.qss')
# if not os.path.exists(EditorStyle):
#     EditorStyle=None
global themes
themes = None

defaultColors= dict(
    name='default',
    code=dict(
        background = (37,37,37),
        keywords = (86,204,105),
        digits = (200,186,84),
        operator = (190,185,128),
        methods = (81,139,179),
        comment = (62,66,68),
        string = (231,155,8),
        includes = (118,118,146),
        type = (141,82,131),
        attribute = (108,148,14),
        directive = (105,85,99),
        brace = (171,169,144),
        default=(169,183,185),
        variable = (206,184,0),
        whitespace=(55,55,55)
    ),
    completer=dict(
        background = (55,59,58),
        background_selected = (143,105,33),
        keywords = (104,207,121),
        methods = (102,181,236),
        type = (173,96,161),
        attribute = (126,166,80),
        directive = (161,132,153),
        default=(194,194,194),
        variable = (206,184,0),
    ),
    houdini_theme='Houdini Dark'
)

def getColors(theme=False):
    global themes
    theme = theme or current_theme
    if not themes:
        themes = get_themes()
        if not theme in themes:
            theme = current_theme or 'Dark'
    return themes.get(theme, defaultColors)


def get_themes():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'colors').replace('\\','/')
    files = os.listdir(path)
    datas = []
    for t in files:
        fullpath = os.path.join(path, t)
        try:
            d = json.load(open(fullpath))
            datas.append(d)
        except:
            pass
    # themes = {d['name']: d for d in datas}
    themes = {}
    for d in datas:
        if 'name' in d:
            themes[d['name']] = d
        else:
            print 'Wrong theme name in %s' % d
    return themes

