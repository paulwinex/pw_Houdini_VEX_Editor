from PySide.QtCore import *
from PySide.QtGui import *
from widgets import template_editor_UIs, template_editor_text_widget
reload(template_editor_UIs)
reload(template_editor_text_widget)
import hqt
import os, json, re

class TemplateEditorClass(QDialog, template_editor_UIs.Ui_templateEditor):
    def __init__(self, parent=None, theme=None):
        super(TemplateEditorClass, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Tool)

        self.template_text_lw = template_editor_text_widget.TemplateEditorTextClass(parent, theme)
        self.text_widget_ly.addWidget(self.template_text_lw)
        self.keyword_le.setParent(None)
        self.keyword_le = KeyWordLineEditClass()
        self.keyword_ly.addWidget(self.keyword_le)

        self.save_btn.clicked.connect(self.save_all)
        self.cancel_btn.clicked.connect(self.reject)
        self.add_btn.clicked.connect(self.add_new_template)
        self.remove_btn.clicked.connect(self.remove_template)
        self.templates_lw.currentItemChanged.connect(self.template_changed)
        self.templates_lw.itemChanged.connect(self.renamed_item)
        self.cursorpos_btn.clicked.connect(self.insert_cursor_position)
        self.setTabOrder(self.keyword_le, self.templates_lw)
        self.open_btn.clicked.connect(self.open_folder)
        @self.keyword_le.returnPressed.connect
        def save_curent():
            s = self.templates_lw.selectedItems()[0]
            self.save_item(s)
        self.splitter.setSizes([100,1000])

        self.fill_template_list()
        self.template_text_lw.setEnabled(0)
        self.keyword_le.setEnabled(0)
        self.cursorpos_btn.setEnabled(0)

    def save_all(self):
        if self.templates_lw.selectedItems():
            self.save_item(self.templates_lw.selectedItems()[0])
        templates = []
        for i in range(self.templates_lw.count()):
            item = self.templates_lw.item(i)
            data = item.data(32)
            templates.append(data)

        if not templates:
            self.reject()
        # check keywords
        err = []
        for j in range(len(templates)):
            for k in range(j+1, len(templates)):
                if templates[k]['keyword'] == templates[j]['keyword']:
                    err.append((templates[k]['name'], templates[j]['name'], templates[j]['keyword']))
        if err:
            msg = 'Warning! Match keywords:\n\n'
            for i, t in enumerate(err):
                msg += '%s: keyword: "%s" in "%s" and "%s"\n' % (i+1, t[2], t[0], t[1])
            msg +='\nFix this conflict!'
            QMessageBox.warning(hqt.houWindow, 'Keyword conflict', msg, QMessageBox.Ok)
            return

        for data in templates:
            self.save_template(data)
        # self.fill_template_list()
        QDialog.accept(self)

    # def load_templates(self):
    #     pass
    #
    # def save_templates(self):
    #     pass
    @staticmethod
    def templates_dir():
        d = os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/')
        if not os.path.exists(d):
            try:
                os.makedirs(d)
            except:
                return
        return d
    @classmethod
    def get_templates(self):
        dir = self.templates_dir()
        if not dir:
            return []
        templates = []
        for t in os.listdir(dir):
            full = os.path.join(dir,t).replace('\\','/')
            data = json.load(open(full))
            data['file'] = full
            templates.append(data)
        return templates

    @classmethod
    def get_live_templates(self):
        templates = self.get_templates()
        out = []
        for t in templates:
            if t['keyword']:
                out.append([t['keyword'], t['text']])
        return out

    def fill_template_list(self):
        templates = self.get_templates()
        self.templates_lw.blockSignals(1)
        self.templates_lw.clear()
        for t in templates:
            item = QListWidgetItem(self.templates_lw)
            item.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setText(t['name'])
            item.setData(32, t)
            self.templates_lw.addItem(item)
        self.templates_lw.blockSignals(0)

    def add_new_template(self):
        default_name = 'New Template'
        self.templates_lw.blockSignals(1)
        item = QListWidgetItem(self.templates_lw)
        item.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        item.setText(default_name)
        data = dict(
            name='New Template',
            keyword='',
            text='',
            file=''
        )
        item.setData(32, data)
        self.templates_lw.addItem(item)
        self.templates_lw.setCurrentItem(item)
        self.templates_lw.blockSignals(0)
        self.template_changed(item, None)

    def save_template(self, data):
        filename = data['file']
        del data['file']
        if filename:
            oldData = json.load(open(filename))
            if oldData == data:
                return
        else:
            name = self.get_filename(data['name'])
            d = self.templates_dir()
            filename = os.path.join(d, name) + '.json'
            while os.path.exists(filename):
                name = self.increment_name(name)
                filename = os.path.join(d, name) + '.json'

        json.dump(data, open(filename, 'w'), indent=4)

    def increment_name(self, name):
        name, ext = os.path.splitext(name)
        m = re.search(r'(.*?)(\d+)$', name)
        if m:
            newname, ind = m.groups()
            return newname + str(int(ind)+1) + ext
        else:
            return name + '1' + ext

    def get_filename(self, name):
        return re.sub('[^A-Za-z0-9]+', '_', name.lower())


    def template_changed(self, new, old):
        self.template_text_lw.setEnabled(1)
        self.keyword_le.setEnabled(1)
        self.cursorpos_btn.setEnabled(1)
        if old:
            self.save_item(old)
        self.load_item(new)

    def save_item(self, item):
        text = self.template_text_lw.toPlainText()
        key = self.keyword_le.text()
        data = item.data(32)
        data['text'] = text
        data['keyword'] = key
        item.setData(32, data)

    def load_item(self, item):
        data = item.data(32)
        self.template_text_lw.setText(data['text'])
        self.keyword_le.setText(data['keyword'])

    def renamed_item(self, item):
        text = item.text()
        data = item.data(32)
        data['name'] = text
        item.setData(32, data)

    def insert_cursor_position(self):
        self.template_text_lw.insertSpecialText('$cursor$')

    def remove_template(self):
        if self.templates_lw.selectedItems():
            item = self.templates_lw.selectedItems()[0]
            if QMessageBox.question(self, 'Close Tab',
                               'Delete this template?\n'+item.data(32)['name'],
                               QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
                path = item.data(32)['file']
                if os.path.exists(path):
                    os.remove(path)
                self.templates_lw.takeItem(self.templates_lw.indexFromItem(item).row())

    def open_folder(self):
        d = self.templates_dir()
        import webbrowser
        webbrowser.open(d)


class KeyWordLineEditClass(QLineEdit):
    def __init__(self):
        super(KeyWordLineEditClass, self).__init__()

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            return
        QLineEdit.keyPressEvent(self, event)

if __name__ == '__main__':
    app = QApplication([])
    w = TemplateEditorClass()
    w.show()
    app.exec_()