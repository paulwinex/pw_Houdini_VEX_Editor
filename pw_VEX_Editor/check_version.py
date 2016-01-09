import urllib2
import re, json, hou, os
import webbrowser

check_version_url =  'https://raw.githubusercontent.com/paulwinex/pw_Houdini_VEX_Editor/master/vexeditorinfo.json'

def str_to_list(str):
    v = re.findall(r'[\d.]+', str)
    if v:
        return [int(x) for x in v[0].split('.')]

def get_last_version():
    try:
        response = urllib2.urlopen(check_version_url)
    except urllib2.HTTPError:
        print 'URL Not Found'
        return
    try:
        data = json.loads(response.read())
        return data
    except ValueError:
        print 'Error Read data'
        return

def get_current_version():
    info_file = os.path.join(os.path.dirname(__file__),'vexeditorinfo.json')
    try:
        d = json.load(open(info_file))
        return d["version"]
    except:
        return [1,0,0]

def check_version():
    # current = str_to_list(v)
    current = get_current_version()
    last = get_last_version()
    if not last:
        r = hou.ui.displayMessage('Error request last version\nCheck it manually?',
                                  buttons=('Yes','No'),
                                  severity=hou.severityType.Message,
                                  default_choice=0,
                                  title='Error auto check')
        if r == 0:
            webbrowser.open('https://github.com/paulwinex')
        return
    if any([x>y for x,y in zip(last['version'],current)]):
        # print 'New version available'
        r = hou.ui.displayMessage('New version available!',
                                  buttons=('Download Page', 'Release Info', 'Cancel'),
                                  severity=hou.severityType.Message,
                                  default_choice=0,
                                  title='New version available')
        if r == 0:
            webbrowser.open(last['download_url'])
        elif r == 1:
            webbrowser.open(last['info_url'])
    else:
        hou.ui.displayMessage('You are using the latest version',
                              buttons=('Ok',),
                              severity=hou.severityType.Message,
                              default_choice=1,
                              title='You have the latest version')
