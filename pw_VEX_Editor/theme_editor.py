try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
import os, glob, json, re, math
try:
    import hqt
except:
    class hqt(object):
        houWindow = None
        @staticmethod
        def get_h14_style(theme):
            return ''

from widgets import theme_editor_UIs
from widgets import color_picker, template_editor_text_widget
reload(template_editor_text_widget)
reload(color_picker)

theme_group_box_text = 'Theme'
houdini_themes = [
    'Houdini Dark',
    'Houdini Light',
    'Houdini Pro'
]

class ThemeEditorClass(QDialog, theme_editor_UIs.Ui_Dialog):
    themesUpdatedSignal = Signal()
    def __init__(self, parent=None):
        super(ThemeEditorClass, self).__init__(parent)
        self.setupUi(self)
        if not __name__ == '__main__':
            self.setWindowFlags(Qt.Tool)
        # widgets
        rampSize = 160
        self.theme = {}
        self.completer = None
        #value slider
        self.value = color_picker.valueSliderClass(rampSize,0.1)
        #color picker
        self.picker = color_picker.colorRampClass(self, rampSize)
        self.picker.scrollSignal.connect(self.value.scrollValue)
        self.value.valueChanged.connect(self.picker.setValue)

        self.picker_ly.addWidget(self.value)
        self.picker_ly.addWidget(self.picker)

        self.new_lb = color_picker.previewColorClass(self, 40)
        self.color_label_ly.addWidget(self.new_lb)

        self.colorList_lw = QListWidget()
        self.scrollArea.setWidget(self.colorList_lw)

        self.previewText_tb = template_editor_text_widget.TemplateEditorTextClass()
        self.previewText_tb.setText(test_text)
        self.preview_ly.addWidget(self.previewText_tb)

        self.current_theme_cbb = ThemesComboBox(self)
        self.themes_cbb_ly.addWidget(self.current_theme_cbb)

        self.houdini_theme_cbb.addItems(houdini_themes)
        self.houdini_theme_cbb.currentIndexChanged.connect(self.set_houdini_style)

        self.color_info = ColorTextValuesWidgetClass(self)
        self.color_info_ly.addWidget(self.color_info)

        #connects
        self.picker.colorChangedSignal.connect(self.color_changed_by_user)
        self.picker.colorChangedSignal.connect(self.update_editor)
        self.current_theme_cbb.currentIndexChanged.connect(self.change_theme)
        self.colorList_lw.itemClicked.connect(self.update_picker)
        self.save_btn.clicked.connect(self.save_theme)
        self.save_as_btn.clicked.connect(self.save_theme_as)
        self.remove_btn.clicked.connect(self.remove_theme)

        #start
        self.splitter.setSizes([250,400])
        self.load_themes()
        self.theme_gb.setTitle(theme_group_box_text)
        self.picker_gb.setEnabled(0)

    def closeEvent(self, event):
        if not self.need_to_change_theme():
            event.ignore()
            # return QDialog.closeEvent(self, event)
        else:
            event.accept()
            return QDialog.closeEvent(self, event)

    def load_themes(self):
        self.current_theme_cbb.clear()
        themes = self.get_themes()
        for theme in themes:
            self.current_theme_cbb.addItem(theme['name'])
            self.current_theme_cbb.setItemData(self.current_theme_cbb.count()-1, theme)
        self.change_theme()

    def themes_path(self):
        return os.path.join(os.path.dirname(__file__), 'colors')

    def get_themes(self):
        path = self.themes_path()
        themes = []
        for c in glob.glob1(path, '*.json'):
            try:
                data = json.load(open(os.path.join(path, c)))
            except:
                continue
            data['path'] = os.path.join(path, c).replace('\\','/')
            themes.append(data)
        return themes

    def change_theme(self):
        i = self.current_theme_cbb.currentIndex()
        self.theme = self.current_theme_cbb.itemData(i)
        self.colorList_lw.clear()
        if not self.theme:
            return
        for widget, array in self.theme.items():
            if isinstance(array, dict):
                for name, color in array.items():
                    item = ColorButtonWidget(widget, name, color)
                    self.colorList_lw.addItem(item)
                    # self.theme[widget][name] = item
        self.previewText_tb.setTheme(self.theme)
        self.picker.setColor(QColor('white'))
        self.picker.setValue(1000)
        self.value.setValue(1000)
        self.theme_gb.setTitle(theme_group_box_text)
        #houdini part
        i =self.houdini_theme_cbb.findText(self.theme['houdini_theme'])
        if not i == -1:
            self.houdini_theme_cbb.setCurrentIndex(i)
            self.set_houdini_style()
            self.theme_gb.setTitle(theme_group_box_text)

        # create completer
        if self.completer:
            self.completer.setParent(None)
        self.completer = CompleterPreviewWidget(self.previewText_tb, self.theme['completer'])
        def resized(event):
            self.completer.move_completer()
            QTextEdit.resizeEvent(self.previewText_tb, event)
        self.previewText_tb.resizeEvent = resized
        # self.completer.show()

    def set_houdini_style(self, it=None):
        if it is None:
            self.setStyleSheet(hqt.get_h14_style(self.theme['houdini_theme']))
        else:
            theme = self.houdini_theme_cbb.currentText()
            self.setStyleSheet(hqt.get_h14_style(theme))
            self.theme_gb.setTitle(theme_group_box_text+'*')


    def color_changed_by_user(self, color, frominfo=False):
        self.theme_gb.setTitle(theme_group_box_text+'*')
        if frominfo:
            self.update_picker(color, not frominfo)
        else:
            self.new_lb.setNextColor(color)
        self.color_info.set_color(color)

    def update_picker(self, color, updateNext=True):
        self.picker_gb.setEnabled(1)
        if not isinstance(color, QColor):
            color = color.color
        h,s,v,a = color.getHsv()
        v = remap(v,0,255,0,1000)
        self.value.blockSignals(1)
        self.value.setValue(v)
        self.value.blockSignals(0)

        self.picker.blockSignals(1)
        self.picker.setColor(color)
        self.picker.setValue(v)
        self.picker.blockSignals(0)

        if updateNext:
            self.new_lb.setPrevColor(color)
        self.new_lb.setNextColor(color)

        self.update_editor(color)
        self.color_info.set_color(color)

    def update_editor(self, color, tmp=None):
        # update item
        it = self.colorList_lw.currentItem()
        if it:
            it.set_color(color)
            self.theme[it.widget][it.name] = [color.red(),color.green(),color.blue()]
        # update editor
            self.previewText_tb.setTheme(self.theme)
            self.completer.update_labels(self.theme['completer'])

    def save_theme(self):
        # print self.theme['name']
        self.theme['houdini_theme'] = self.houdini_theme_cbb.currentText()
        theme = self.theme.copy()
        del theme['path']
        t = json.dumps(theme, indent=4)
        for x in re.findall(r'\[.*?\]', t, re.DOTALL):
            t = t.replace(x,x.replace(' ','').replace('\n',''))
        # json.dump(theme, open(self.theme['path'], 'w'), indent=4)
        open(self.theme['path'], 'w').write(t)
        self.current_theme_cbb.setItemData(self.current_theme_cbb.count()-1, self.theme)
        self.theme_gb.setTitle(theme_group_box_text)

    def need_to_change_theme(self):
        import hou
        if '*' in self.theme_gb.title():
            if hou.applicationVersion()[0] >= 16:
                a = QMessageBox.question(self, 'Unsaved changes', 'Undo changes in the theme "%s"?' % self.theme['name'])
            else:
                a = QMessageBox.question(self, 'Unsaved changes',
                                         'Undo changes in the theme "%s"?' % self.theme['name'], QMessageBox.Yes | QMessageBox.No)
            return a == QMessageBox.Yes
        return True

    def save_theme_as(self):
        name = QInputDialog.getText(self, 'New Theme Name', 'Enter new theme name' )
        if name[1]:
            path = self.themes_path()
            name = name[0]
            filename = re.sub('[^A-Za-z0-9]+', '_', name.lower()) + '.json'
            if filename in os.listdir(path):
                QMessageBox.warning(self, 'File exists', 'Filename already exists:\n' + filename)
                self.save_theme_as()
                return
            theme = self.theme.copy()
            theme['name'] = name
            del theme['path']
            filepath = os.path.join(path, filename)
            json.dump(theme, open(filepath, 'w'), indent=4)
            self.load_themes()
            index = self.current_theme_cbb.findText(name)
            if not index == -1:
                self.current_theme_cbb.setCurrentIndex(index)
            self.themesUpdatedSignal.emit()

    def remove_theme(self):
        import hou
        if hou.applicationVersion()[0] >= 16:
            res = QMessageBox.question(hqt.houWindow, 'Remove Theme', 'Remove theme "%s"?' % self.theme['name']) == QMessageBox.Yes
        else:
            res = QMessageBox.question(hqt.houWindow, 'Remove Theme',
                                       'Remove theme "%s"?' % self.theme['name'], QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes
        if res:
            try:
                os.remove(self.theme['path'])
            except:
                QMessageBox.warning(hqt.houWindow, 'Error', 'Error remove file')
            self.load_themes()
            self.themesUpdatedSignal.emit()


def remap(value, oldMin, oldMax, newMin, newMax):
    leftSpan = oldMax - oldMin
    rightSpan = newMax - newMin
    valueScaled = float(value - oldMin) / float(leftSpan)
    return newMin + (valueScaled * rightSpan)

class ColorButtonWidget(QListWidgetItem):
    def __init__(self, widget, name, color):
        super(ColorButtonWidget, self).__init__()
        self.color = color
        self.widget = widget
        self.name = name

        self.setText(' | '.join([widget.title(), name.title()]))

        self.set_color(color)

    def set_color(self, color):
        if isinstance(color, list):
            color = QColor(*color)
        self.color = color
        pix = QPixmap(16,16)
        pix.fill(color)
        self.setIcon(QIcon(pix))


class ThemesComboBox(QComboBox):
    def __init__(self, parent):
        super(ThemesComboBox, self).__init__(parent)
        self.par = parent
    def mousePressEvent(self, ev):
        if self.par.need_to_change_theme():
            super(ThemesComboBox, self).mousePressEvent(ev)


class ColorTextValuesWidgetClass(QWidget):
    colorChangedSignal = Signal(QColor)
    def __init__(self, parent=None):
        super(ColorTextValuesWidgetClass, self).__init__()
        self.p = parent
        self.ly = QVBoxLayout(self)

        # grid
        self.gridLayout = QGridLayout()
        self.label_2 = QLabel('HEX')
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.hex_le = ColorInfoLineEditClass(r'^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', self)
        self.hex_le.applyColorSignal.connect(self.create_color)
        self.gridLayout.addWidget(self.hex_le, 0, 1, 1, 1)
        self.label_3 = QLabel('RGB')
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.rgb_le = ColorInfoLineEditClass(r'^\d{1,3}[, ]{1}\d{1,3}[, ]{1}\d{1,3}$', self)
        self.rgb_le.applyColorSignal.connect(self.create_color)
        self.gridLayout.addWidget(self.rgb_le, 1, 1, 1, 1)
        self.label_8 = QLabel('HSV')
        self.gridLayout.addWidget(self.label_8, 2, 0, 1, 1)
        self.hsv_le = ColorInfoLineEditClass(r'^\d{1,3}[, ]{1}\d{1,3}[, ]{1}\d{1,3}$', self)
        self.hsv_le.applyColorSignal.connect(self.create_color)
        self.gridLayout.addWidget(self.hsv_le, 2, 1, 1, 1)
        self.ly.addLayout(self.gridLayout)
        self.color = None

        for le in self. hex_le, self.rgb_le, self.hsv_le:
            le.returnPressed.connect(self.create_color)

    def set_color(self, color=None):
        if not color:
            color = self.color
        else:
            self.color = color
        self.hex_le.setText(color.name())
        self.rgb_le.setText('%s , %s , %s' % (color.red(), color.green(), color.blue()))
        self.hsv_le.setText('%s , %s , %s' % (color.hue(), int(remap(color.saturation(),0,255,0,100)) , int(remap(color.value(),0,255,0,100)) ))

    def create_color(self):
        for le in self. hex_le, self.rgb_le, self.hsv_le:
            le.blockSignals(1)
        sender = self.sender()
        color = self.color
        if sender is self.rgb_le:
            rgb = self.split_line(sender.text())
            if rgb:
                color = QColor.fromRgb(*[min(255, x) for x in rgb])
                self.color = color
        elif sender is self.hsv_le:
            hsv = self.split_line(sender.text())
            if hsv:

                color = QColor.fromHsv(min(hsv[0], 360), math.ceil(remap(hsv[1],0,100,0,255)), math.ceil(remap(hsv[2],0,100,0,255)))
                self.color = color
        elif sender == self.hex_le:
            hex = self.hex_le.text()
            if not hex[0] == '#':
                hex = '#'+hex
            color = QColor(hex)
            self.color = color
        self.p.color_changed_by_user(color, True)

        for le in self. hex_le, self.rgb_le, self.hsv_le:
            le.blockSignals(0)

    def split_line(self, text):
        if ',' in text:
            clr = text.split(',')
        else:
            clr = text.split(' ')
        try:
            rgb = [int(x) for x in clr]
            return rgb
        except:
            return

class ColorInfoLineEditClass(QLineEdit):
    applyColorSignal = Signal()
    def __init__(self, regex, parent):
        super(ColorInfoLineEditClass, self).__init__(parent)
        self.editingFinished.connect(self.applyColorSignal.emit)
        regexp = QRegExp(regex)
        validator = QRegExpValidator(regexp)
        self.setValidator(validator)


    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return, Qt.Key_Enter ]:
            self.applyColorSignal.emit()
            return
        QLineEdit.keyPressEvent(self, event)

class CompleterPreviewWidget(QWidget):
    style='''
    background-color: rgb{bgcolor};
    color: rgb{color};
    font-size:14px;
    border: none;
    padding: 2px 5px 2px 5px;
    '''
    def __init__(self, parent, items):
        super(CompleterPreviewWidget, self).__init__(parent)
        self.p = parent
        self.ly = QVBoxLayout(self)
        self.ly.setContentsMargins(2,2,2,2)
        self.ly.setSpacing(0)
        self.labels = {}
        self.colors = {}
        for name, color in items.items():
            if name in ['background', 'background_selected']:
                continue
            l = CompleterLabel(name.title(), self)
            l.setObjectName(name)
            l.setMinimumWidth(150)
            self.labels[name] = l
            self.ly.addWidget(l)

        self.update_labels(items)
        self.show()
        QTimer.singleShot(100,self.move_completer)


    def move_completer(self, *args):
        geoPar = self.p.geometry()
        x = geoPar.width() - self.width() - 10
        y = geoPar.height() - self.height() - 10 - (14*int(self.p.horizontalScrollBar().isVisible()))
        self.move(x, y)

    def update_labels(self, colors=None):
        colors = colors or self.colors
        self.colors = colors
        bg = colors['background']
        sbg = colors['background_selected']
        for name, color in colors.items():
            if name in ['background', 'background_selected']:
                continue
            if name in self.labels:
                if self.labels[name].selected:
                    s = self.style.format(bgcolor=tuple(sbg),
                                  color=tuple(colors['default']))
                else:
                    s = self.style.format(bgcolor=tuple(bg),
                                  color=tuple(color))
                self.labels[name].setStyleSheet(s)


class CompleterLabel(QLabel):
    def __init__(self, text, parent):
        super(CompleterLabel, self).__init__(text)
        self.p =  parent
        self.selected = False
    def mousePressEvent(self, event):
        for l in self.p.labels.values():
            l.selected = False
        self.selected = True
        self.p.update_labels()
        super(CompleterLabel, self).mousePressEvent(event)
    def deselect(self):
        self.selected=False

test_text = '''#pragma label Some Label
#include <extrafile.h>

// Comment
vector variable = { 0, 1, 0 };
float variable2 = ch('parameter');

vector	attr = @attribute;
int		result = function();
string str = "string value";
// Comment

for (int i = 0; i < steps; i++)
{
    foreach (x; result) {
        count += $GLOBAL_VAR;
    }

}

'''

if __name__ == '__main__':
    app = QApplication([])
    w = ThemeEditorClass()
    w.show()
    app.exec_()