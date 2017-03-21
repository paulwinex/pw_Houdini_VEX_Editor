try:
    from PySide.QtCore import *
    from PySide.QtGui import *
except:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
import re, os, hou
from vexSyntax import design, syntaxHighLighter
import completer_widget
from .. autocomplete import vex_parser
from .. autocomplete import keywords as completer_keywords
from vexSyntax import keywords as syntax_keyword
from templates import live_templates
# from .. import vex_settings
# reload(vex_settings)
reload(design)
reload(syntaxHighLighter)
reload(completer_keywords)
reload(syntax_keyword)
reload(vex_parser)
reload(completer_widget)
reload(live_templates)


indentLen = 4
minimumFontSize = 8
maximumFontSize = 60
font_name = 'Lucida Console'
# font_name = 'Courier New'

escapeButtons = [Qt.Key_Return, Qt.Key_Enter, Qt.Key_Left, Qt.Key_Right, Qt.Key_Home, Qt.Key_End,
                 Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Delete, Qt.Key_Insert, Qt.Key_Escape,
                 Qt.Key_Space]


class VEXEditorInputWidget(QTextEdit):
    saveSignal = Signal()
    messageSignal = Signal(str)
    helpSignal = Signal(str)
    def __init__(self, parent):
        QTextEdit.__init__(self, parent)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setAcceptRichText(False)
        self.setAcceptDrops(True)
        self.container = parent

        self.bg = [0,0,0]
        from .. import vex_settings
        self.s = vex_settings.EditorSettingsClass()
        self.fs = self.s.get_value('font_size',vex_settings.default_data['font_size'])
        self.fn = self.s.get_value('font_name',vex_settings.default_data['font_name'])
        self.document().setDefaultFont(QFont(font_name, minimumFontSize, QFont.Normal))
        metrics = QFontMetrics(self.document().defaultFont())
        self.setTabStopWidth(4 * metrics.width(' '))

        self.desk = QApplication.desktop()
        self.setTextEditFontSize(self.fs)
        self.completer = completer_widget.CompleterListClass(parent, self)

        self.cursorPositionChanged.connect(self.parse_help_line)

        self.use_completer = False
        # self.use_help_window = True
        self.last_help = None
        self.live_templates = []
        self.update_live_templates()
        self.update_from_settings()



    def update_live_templates(self):
        from pw_VEX_Editor.template_editor import TemplateEditorClass
        self.live_templates = TemplateEditorClass.get_live_templates()

    def apply_style(self, theme=None, colors=None):
        # get style
        if not colors:
            colors = design.getColors(theme)

        # editor bg
        color = colors['code']['background']
        self.bg = color
        self.setTextEditFontSize()
        # syntax hightlighter
        self.blockSignals(True)
        # colors = None
        self.hgl = syntaxHighLighter.VEXHighlighterClass(self, colors)
        self.blockSignals(False)
        # completer
        if self.use_completer:
            self.completer.updateStyle(colors)

    def hideEvent(self, *args, **kwargs):
        if self.use_completer:
            self.completer.hideMe()
        QTextEdit.hideEvent(self, *args, **kwargs)

    def focusOutEvent(self, event):
        QTextEdit.focusOutEvent(self, event)
        if self.use_completer:
            if not QApplication.activeWindow() is self.completer:
                self.completer.hideMe()

    def addRemoveComments(self, text):
        result = text
        ofs = 0
        if text.strip():
            lines = text.split('\n')
            ind = 0
            while not lines[ind].strip():
                ind += 1
            if lines[ind].strip()[0:2] == '//': # remove comment
                result = '\n'.join([x.replace('//','',1) for x in lines])
                ofs = -1
            else:   # add comment
                result = '\n'.join(['//'+x for x in lines ])
                ofs = 1
        return result, ofs

    def duplicate(self):
        self.document().documentLayout().blockSignals(True)
        cursor = self.textCursor()
        if cursor.hasSelection(): # duplicate selected
            sel = cursor.selectedText()
            end = cursor.selectionEnd()
            cursor.setPosition(end)
            cursor.insertText(sel)
            cursor.setPosition(end,QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
        else: # duplicate line
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfLine,QTextCursor.KeepAnchor)
            line = cursor.selectedText()
            cursor.clearSelection()
            cursor.insertText('\n'+line)
            self.setTextCursor(cursor)
        self.document().documentLayout().blockSignals(False)

    def removeTabs(self, text):
        lines = text.split('\n')
        new = []
        pat = re.compile("^ .*")
        for line in lines:
            line = line.replace('\t', ' '*indentLen)
            for _ in range(4):
                if pat.match(line):
                    line = line[1:]
            new.append(line)
        return '\n'.join(new)

    def addTabs(self, text):
        lines = [(' '*indentLen)+x for x in text.split('\n')]
        return '\n'.join(lines)

    def selectBlocks(self):
        self.document().documentLayout().blockSignals(True)
        cursor = self.textCursor()
        start, end = cursor.selectionStart(), cursor.selectionEnd()
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        self.document().documentLayout().blockSignals(False)

    def getSelection(self):
        cursor = self.textCursor()
        text = cursor.selection().toPlainText()
        return text

    def wheelEvent(self, event):

        if event.modifiers() == Qt.ControlModifier:
            if event.delta() > 0:
                self.changeFontSize(True)
            else:
                self.changeFontSize(False)
        else:
            QTextEdit.wheelEvent(self, event)
        self.container.lineNum.update()

    def changeFontSize(self, up):
        if up:
            self.fs = min(maximumFontSize, self.fs+1)
        else:
            self.fs = max(minimumFontSize, self.fs - 1)
        self.setTextEditFontSize(self.fs)
        self.messageSignal.emit('Font Size: %s' % self.fs)

    def setTextEditFontSize(self, size=None):
        size = size or self.fs
        style = self.styleSheet() +'''QTextEdit
    {
        font-size: %spx;
        font-family: %s;
        background-color: rgb(%s, %s, %s);
    }''' % (size, self.fn, self.bg[0],self.bg[1],self.bg[2],)
        self.setStyleSheet(style)

    # def dragMoveEvent(self, event):
    #     print 'drag', event.pos()
    #     QTextEdit.dragMoveEvent(self, event)

    def getFontSize(self):
        s = self.font().pointSize()
        return s

    def setFontSize(self,size):
        if size > minimumFontSize:
            self.fs = size
            self.setTextEditFontSize(self.fs)

    def moveSelected(self, inc):
        cursor = self.textCursor()
        if cursor.hasSelection():
            self.document().documentLayout().blockSignals(True)
            self.selectBlocks()
            start, end = cursor.selectionStart(), cursor.selectionEnd()
            text = cursor.selection().toPlainText()
            cursor.removeSelectedText()
            if inc:
                newText = self.addTabs(text)
            else:
                newText = self.removeTabs(text)
            cursor.beginEditBlock()
            cursor.insertText(newText)
            cursor.endEditBlock()
            newEnd = cursor.position()
            cursor.setPosition(start)
            cursor.setPosition(newEnd, QTextCursor.KeepAnchor)
            self.document().documentLayout().blockSignals(False)
            self.setTextCursor(cursor)
            self.update()

    def keyPressEvent(self, event):
        # linux fix
        if event.key() == Qt.Key_NumLock:
            return QTextEdit.keyPressEvent(self, event)

        self.container.lineNum.update()
        parse = 0
        parse_help = 1
        cursor = self.textCursor()
        use_live_template = True
        # apply complete
        if event.modifiers() == Qt.NoModifier and event.key() in [Qt.Key_Return , Qt.Key_Enter]:
        # if event.key() in [Qt.Key_Return , Qt.Key_Enter]:
            if self.use_completer and self.completer.isVisible():
                self.completer.apply_current_complete()
                self.completer.hideMe()
                return
            # auto indent
            else:
                add = self.get_current_indent()
                if add:
                    QTextEdit.keyPressEvent(self, event)

                    cursor.insertText(add)
                    self.setTextCursor(cursor)
                    return
        # online help
        # elif event.key() == Qt.Key_F1:
        #     self.open_context_help()
        #     return

        # remove 4 spaces
        if event.modifiers() == Qt.NoModifier and event.key() == Qt.Key_Backspace:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine,QTextCursor.KeepAnchor)
            line = cursor.selectedText()
            if line:
                p = r"    $"
                m = re.search(p, line)
                if m:
                    cursor.removeSelectedText()
                    line = line[:-3]
                    cursor.insertText(line)
                    self.setTextCursor(cursor)
            parse = 1
        #comment
        elif event.modifiers() == Qt.AltModifier and event.key() == Qt.Key_Q:
            self.commentSelected()
            return
        # execute selected
        elif event.modifiers() == Qt.ControlModifier and event.key() in [Qt.Key_Return , Qt.Key_Enter]:
            self.saveSignal.emit()
        # ignore Shift + Enter
        elif event.modifiers() == Qt.ShiftModifier and event.key() in [Qt.Key_Return , Qt.Key_Enter]:
            return
        # duplicate
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_D:
            self.duplicate()
            self.update()
            return
        # increase indent
        elif event.key() == Qt.Key_Tab:
            if self.use_completer:
                if self.completer.isVisible():
                    # self.completer.apply_current_complete()
                    self.completer.hideMe()
                    # return
                    # if use_live_template:
                    #     self.live_templates(cursor, event)
                    #     use_live_template = False
                    # return
            if cursor.selection().toPlainText():
                self.selectBlocks()
                self.moveSelected(True)
                return
            else:
                if self.accept_live_templates(cursor, event):
                    use_live_template = False
                    return
                self.insertPlainText (' ' * indentLen)
                return
        # decrease indent
        elif event.key() == Qt.Key_Backtab:
            self.selectBlocks()
            self.moveSelected(False)
            # if self.completer:
            #     self.completer.update_complete_list()
            return
        # start of line
        elif event.key() == Qt.Key_Home:
            # QTextEdit.keyPressEvent(self, event)
            pos = cursor.position()
            sel = cursor.selectedText()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfLine,QTextCursor.KeepAnchor)
            line = cursor.selectedText()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            startLine = endpos = cursor.position()
            # check
            pre_space = re.search(r'^\s+', line)
            if pre_space:
                endpos = cursor.position()+len(pre_space.group(0))
                if endpos == pos:
                    endpos = startLine

            if event.modifiers() == Qt.ShiftModifier:
                if sel:
                    c = self.textCursor()
                    c.setPosition(endpos,QTextCursor.KeepAnchor)
                    self.setTextCursor(c)
                    return
                else:
                    cursor.setPosition(pos)
                    cursor.setPosition(endpos,QTextCursor.KeepAnchor)
            else:
                cursor.setPosition(endpos,QTextCursor.MoveAnchor)
            self.setTextCursor(cursor)
            # QTextEdit.keyPressEvent(self, event)
            return
        # close completer
        elif event.key() in escapeButtons:
            if self.use_completer:
                self.completer.hideMe()
            self.setFocus()
        # go to completer
        elif event.key() == Qt.Key_Down or event.key() == Qt.Key_Up:
            if self.completer.isVisible():
                self.completer.activateCompleter(event.key())
                return
            else:
                self.setFocus()
        # just close completer
        elif not event.modifiers() == Qt.NoModifier and not event.modifiers() == Qt.ShiftModifier:
            self.completer.hideMe()
        else:
            parse = 1

        # if not self.auto_brackets(event):
        if not self.auto_brackets(event):
            QTextEdit.keyPressEvent(self, event)

        # start parse text
        if parse and event.text() and self.use_completer:
            self.parse_code()
            # self.open_completer()
        else:
            if self.use_completer:
                self.completer.hideMe()
        # if self.use_help_window:
        self.parse_help_line()

    def parse_code(self):
        cursor = self.textCursor()
        pos = cursor.position()
        text = self.toPlainText()
        line = text[:pos].split('\n')[-1]
        if line:
            self.open_completer(line, text, pos)

    def open_completer(self, line, text, pos):
        # if not self.use_completer:
        #     return
        # curson = self.textCursor()
        # pos = curson.position()
        # text = self.toPlainText()
        # line = text[:pos].split('\n')[-1]
        # if line:
            # include files
            if line.strip().startswith('#include'):
                #f = re.findall(r'#include <([.\w\d]*)$', line)
                f = re.findall(r'#include (<|"|\')([.\w\d]*)$', line)
                if f:
                    word = f[0][1]
                    files = vex_parser.includes.get_include_file_list()
                    if word:
                        files = [x for x in files if x.startswith(word)]
                    names = []
                    for f in files:
                        names.append(vex_parser.wordCompletion(f, word, vex_parser.wordCompletion.DEFINITION))
                    self.completer.update_complete_list(names)
                    return
            for cnx in completer_keywords.context_complete:
                p = re.findall(cnx + r'(\w*)$', line)
                if p:
                    word = p[0]
                    if word:
                        comps = [x for x in completer_keywords.context_complete[cnx] if x.startswith(word)]
                    else:
                        comps = completer_keywords.context_complete[cnx]
                    names = []
                    for c in comps:
                        names.append(vex_parser.wordCompletion(c, word, vex_parser.wordCompletion.DEFINITION))
                    self.completer.update_complete_list(names)
                    return

            s = line.split()
            if s:
                s = s[-1]
                # is directive
                m = re.match('#(\w*)$', line)
                if m:
                    names = []
                    word = m.group(1)
                    if not word:
                        words = syntax_keyword.syntax['directive']+syntax_keyword.syntax['ifdirective']
                    else:
                        words = [x for x in syntax_keyword.syntax['directive']+syntax_keyword.syntax['ifdirective'] if x.startswith(word)]
                    for a in words:
                        names.append(vex_parser.wordCompletion('#'+a, s, vex_parser.wordCompletion.DEFINITION))
                    self.completer.update_complete_list(names)
                    return
                # channel function
                if self.container.parm:
                    # if not self.container.parn.node().type()
                    chan = re.findall(r"""ch([vispf]{0,1}|ramp)\s*\(['"](\w+)$""", line)
                    if chan:
                        if chan[0][1]:
                            p = chan[0][1]
                            names = []
                            node = self.container.parm.node()
                            parms = [x.name() for x in node.parms() + node.parmTuples()]
                            compParms = [x for x in list(set(parms)) if not x == p and x.startswith(p)]
                            for a in sorted(compParms):
                                names.append(vex_parser.wordCompletion(a, p, vex_parser.wordCompletion.ATTRIBUTE))
                            self.completer.update_complete_list(names)
                            return
                # global variables
                var = re.findall(r'\$\w*$', s)
                parent = self.parent()
                if var and parent.parm:
                    # elif s[0] == '$' and
                    s = var[0]
                    names = []
                    node = parent.parm.node()

                    if node.type().name() == 'inline':
                        # for inline node
                        if s == '$':
                            inp = [x for x in sorted(list(node.inputNames()+node.outputNames()), key=lambda x:x.lower()) if not x == 'next']
                        else:
                            inp = [x for x in sorted(list(node.inputNames()+node.outputNames()), key=lambda x:x.lower()) if not x == 'next' and x.lower().startswith(s[1:].lower())]

                        names = [vex_parser.wordCompletion('$'+x, s, vex_parser.wordCompletion.VARIABLE) for x in inp]
                    else:
                        vrmaps = []
                        try:
                            vrmaps = [x.split()[-1] for x in node.geometry().findGlobalAttrib('varmap').strings()]
                        except:
                            pass
                        vrmaps += completer_keywords.variables

                        if s == '$':
                            words = vrmaps
                        else:
                            words = [x for x in vrmaps if x.lower().startswith(s[1:].lower())]

                        for a in words:
                            names.append(vex_parser.wordCompletion('$'+a, s, vex_parser.wordCompletion.VARIABLE))


                    self.completer.update_complete_list(names)
                    return

            w = re.search(r'[^\w@]?(@?[a-zA-Z_]*?[a-zA-Z_0-9]*)$', line).group(1)
            if w:
                # is attribute ?
                if w[0] == '@': # attributes
                    w = w[1:]
                    p = vex_parser.AttributesParser(w, self.container.parm)
                    names = p.get_names()
                    self.completer.update_complete_list(names)
                else:
                    # default completer
                    p = vex_parser.Parser.parse(text)
                    names = p.get_names_at(pos, w)
                    self.completer.update_complete_list(names)
            else:
                self.completer.hideMe()
        # else:
        #     self.completer.hideMe()

    def parse_help_line(self, line=None):
        # print QApplication.mouseButtons()
        if self.textCursor().selectedText():
            # self.helpSignal.emit('')
            return
        cursor = self.textCursor()
        pos = cursor.position()
        text = self.toPlainText()
        # line = text[:pos].split('\n')[-1]
        func = vex_parser.Parser.parse_help_line(text[:pos])
        hlp = completer_keywords.get_functions_help_window(func)
        if hlp:
            # if not self.last_help == hlp:
            self.helpSignal.emit(hlp)
            QTimer.singleShot(10,self.ensureCursorVisible)
                # self.last_help = hlp
        else:
            self.helpSignal.emit('')

    def commentSelected(self):
        cursor = self.textCursor()
        self.document().documentLayout().blockSignals(True)
        self.selectBlocks()
        pos = cursor.position()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.setPosition(end,QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine,QTextCursor.KeepAnchor)
        text = cursor.selection().toPlainText()
        self.document().documentLayout().blockSignals(False)
        # cursor.removeSelectedText()
        text, offset = self.addRemoveComments(text)
        cursor.insertText(text)
        cursor.setPosition(min(pos+offset, len(self.toPlainText())))
        self.setTextCursor(cursor)
        self.update()

    def move_completer(self):
        if not self.use_completer:
            return
        # self.p.out.showMessage('move')
        rec = self.cursorRect()
        # pt = self.mapToGlobal(QPoint(rec.bottomRight().x(), rec.y()+self.completer.lineHeight))
        pt = self.mapToGlobal(rec.bottomRight())
        y=x=0
        if self.completer.isVisible() and self.desk:
            currentScreen = self.desk.screenGeometry(self.mapToGlobal(rec.bottomRight()))
            futureCompGeo = self.completer.geometry()
            futureCompGeo.moveTo(pt)
            if not currentScreen.contains(futureCompGeo):
                i = currentScreen.intersect(futureCompGeo)
                x = futureCompGeo.width() - i.width()
                y = futureCompGeo.height()+self.completer.lineHeight if (futureCompGeo.height()-i.height())>0 else 0

        pt = self.mapToGlobal(rec.bottomRight()) + QPoint(10-x, -y)

        self.completer.move(pt)

    def insert_text(self, comp):

        cursor = self.textCursor()
        self.document().documentLayout().blockSignals(True)
        cursor.insertText(comp.complete)
        cursor = self.fixLine(cursor, comp)
        if vex_parser.wordCompletion.FUNCTION == comp.type:
            cursor = self.add_method_brackets(cursor)
        self.document().documentLayout().blockSignals(False)
        self.setTextCursor(cursor)
        self.update()

    def add_method_brackets(self, cursor):
        pos = cursor.position()
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine,QTextCursor.KeepAnchor)
        line = cursor.selectedText()
        add = False
        if line:
            line = line.split()
            if line:
                if line[0] != '(':
                    add= True
        else:
            add=True
        cursor.setPosition(pos)
        if add:
            cursor.insertText('()')
            cursor.setPosition(cursor.position()-1)
        return cursor

    def fixLine(self, cursor, comp):
        pos = cursor.position()
        linePos = cursor.positionInBlock()

        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine,QTextCursor.KeepAnchor)
        line = cursor.selectedText()
        cursor.removeSelectedText()

        start = line[:linePos]
        end = line[linePos:]
        before = start[:-len(comp.name)]
        br = ''
        ofs = 0
        res = before + comp.name + br + end

        # self.document().documentLayout().blockSignals(False)
        cursor.beginEditBlock()
        cursor.insertText(res)
        cursor.endEditBlock()
        cursor.clearSelection()
        cursor.setPosition(pos+ofs,QTextCursor.MoveAnchor)
        return cursor

    def mousePressEvent(self, event):
        if self.use_completer:
            self.completer.hideMe()
        if  event.button() == Qt.MouseButton.RightButton:
            menu = self.createStandardContextMenu()
            menu.exec_(event.globalPos())
        self.container.lineNum.update()
        QTextEdit.mousePressEvent(self, event)

    def get_current_indent(self):
        cursor = self.textCursor()
        auto = self.char_before_cursor() == '{'
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine,QTextCursor.KeepAnchor)
        line = cursor.selectedText()
        result = ''
        if line.strip():
            p = r"(^\s*)"
            m = re.search(p, line)
            if m:
                result = m.group(0)
            if auto:
                result += '    '
        return result

    def char_before_cursor(self, count=1):
        cursor = self.textCursor()
        pos = cursor.position()
        p = min(max(0, pos-count), self.document().characterCount()-1)
        cursor.setPosition(p, QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        # cursor.setPosition(pos)

        return text
        # if pos:
        #     text = self.toPlainText()
        #     return text[pos-1]

    def char_after_cursor(self, count):
        cursor = self.textCursor()
        pos = cursor.position()
        p = max(0,min(pos+count, self.document().characterCount()-1))
        cursor.setPosition(p, QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        return text

    def auto_brackets(self, event):
        if event.key() == Qt.Key_Backspace:
            # remove
            cursor = self.textCursor()
            if not cursor.atBlockEnd():
                c = self.char_before_cursor(1)
                for t in live_templates.auto_templates:
                    if c == t[0]:
                        pos = cursor.position()
                        cursor.setPosition(pos+1, QTextCursor.KeepAnchor)
                        c2 = cursor.selectedText()
                        if c2 == t[1]:
                            cursor.setPosition(pos-1)
                            cursor.setPosition(pos+1, QTextCursor.KeepAnchor)
                            cursor.removeSelectedText()
                            self.setTextCursor(cursor)
                            return True

        else:
            # add
            char = event.text()
            for t in live_templates.auto_templates:
                if char == t[0]:
                    cursor = self.textCursor()
                    cursor.insertText(t[0] + t[1])
                    cursor.setPosition(cursor.position() - len(t[1]))
                    self.setTextCursor(cursor)
                    return True
                elif char == t[1]:
                    if t[1] == self.char_after_cursor(len(t[1])):
                        cursor = self.textCursor()
                        cursor.setPosition(max(cursor.position() + len(t[1]), self.document().characterCount()-1))
                        self.setTextCursor(cursor)
                        return True

    def accept_live_templates(self, cursor, event, remove=False, auto=False):
        # templates = live_templates.tab_templates
        for t in self.live_templates:
            c = self.char_before_cursor(len(t[0])).strip()
            if c == t[0]:
                pos = cursor.position()
                # remove kay word
                cursor.setPosition(pos-len(t[0]), QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
                # add template
                cursor.insertText(t[1].replace('$cursor$',''))
                offs = max(t[1].find('$cursor$'),0)
                cursor.setPosition(pos+offs-len(t[0]))
                self.setTextCursor(cursor)
                return True

    def text(self):
        return self.toPlainText()

    def update_from_settings(self):
        s = self.s.get_settings()
        from .. import vex_settings
        self.fs = s.get('font_size',vex_settings.default_data['font_size'])
        self.fn = s.get('font_name',vex_settings.default_data['font_name'])
        self.setTextEditFontSize()
        self.show_white_spaces(s.get('show_whitespaces',vex_settings.default_data['show_whitespaces']))
        self.use_completer = s.get('autocompleter', vex_settings.default_data['autocompleter'])
        # self.use_help_window = s.get('helpwindow', vex_settings.default_data['helpwindow'])

    def show_white_spaces(self, state):
        option =  self.document().defaultTextOption()
        if state:
            option.setFlags(option.flags() | QTextOption.ShowTabsAndSpaces)
            option.setFlags(option.flags() | QTextOption.AddSpaceForLineAndParagraphSeparators)
        else:
            option.setFlags(option.flags() & ~QTextOption.ShowTabsAndSpaces)
            option.setFlags(option.flags() & ~QTextOption.AddSpaceForLineAndParagraphSeparators)
        self.document().setDefaultTextOption(option)

    def select_word(self, pattern, index):
        text = self.toPlainText()
        if not pattern in text:
            return 0
        cursor = self.textCursor()
        # indexis = [(m.start(0), m.end(0)) for m in re.finditer(self.fixRegextSymbols(pattern), text)]
        indexis = [(m.start(0), m.end(0)) for m in re.finditer(pattern, text)]
        lastIndex = 0
        if not indexis:
            return 0
        for i in indexis:
            if i[1] > index:
                cursor.setPosition(i[0])
                cursor.setPosition(i[1], QTextCursor.KeepAnchor)
                lastIndex = i[1]
                break
        self.setTextCursor(cursor)
        return lastIndex

    def replace_selected(self, rep):
        cursor = self.textCursor()
        sel = cursor.selectedText()
        if sel:
            l = len(sel)
            cursor.removeSelectedText()
            cursor.insertText(rep)
            self.setTextCursor(cursor)
            return l

    def replace_all(self, src, trg):
        text = self.toPlainText()
        text = text.replace(src, trg)
        self.setText(text)
