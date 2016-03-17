import os, re
import keywords
reload(keywords)
import waiting_dialog
reload(waiting_dialog)
# from PySide.QtCore import QTimer


# generate completes
def generate():
    d = waiting_dialog.WaitingDialogClass()
    d.generate()

class Include(object):
    def __init__(self):
        self.includes = {}

    def get_include_file(self, filename):
        if filename in self.includes:
            # check modify date
            # if file changed - reload file
            return self.includes[filename]['block']
        else:
            path = self.get_file(filename)
            if os.path.exists(path):
                text = open(path).read()
                p = Parser.parse(text)
                self.includes[filename] = {'block': p}
                return p
            else:
                # print 'Include file not found'
                return Parser()

    def get_file(self, filename):
        paths = self.includes_paths()
        for path in paths:
            if os.path.exists(path) and os.path.isdir(path):
                if filename in os.listdir(path):
                    f = os.path.join(path, filename).replace('\\','/')
                    if os.path.exists(f):
                        return f
        return ''

    def includes_paths(self):
        path_list = []
        hfs = os.getenv('HFS')
        includes = os.path.join(hfs, 'houdini/vex/include').replace('\\','/')
        path_list.append(includes)

        vars = ['HOUDINI_VEX_PATH']
        for v in vars:
            var = os.getenv(v)
            if var:
                paths = var.split(os.pathsep)
                for p in paths:
                    if os.path.isdir(p):
                        path_list.append(p.replace('\\','/'))
        return path_list

    def get_include_file_list(self):
        path_list = self.includes_paths()
        names = []
        for path in path_list:
            names += os.listdir(path)
        return names

# define includes Class
includes = Include()


class Comment():
    def __init__(self):
        self.text = ''
        self.s = 0  # start
        self.e = 0  # end

S_CODE,S_INLINE,S_MULTLINE = range (3)


class Parser(object):
    count = 0
    def __init__(self, parent_block=None, context=None):
        self.__class__.count += 1           # id of all blocks
        self.start = 0                      # start index
        self.end = 0                        # end index
        self.id = self.__class__.count      # block id
        self.code = ''                      # text code
        self.comments = []                  # comments
        self.blocks = []                    # inside blocks
        self.parent = parent_block          # parent block
        self.var = dict(                    # variables and functions
            func=[],
            vars = []
        )
        self.context = context              # node context

    def __del__(self):
        self.__class__.count -= 1

    def split_lines(self, string):
        if isinstance(string, str):
            return string.split('\n')
        else:
            return string

    def join_lines(self, array):
        if isinstance(array, list):
            return '\n'.join(array)
        else:
            return array

    def remove_comments(self, text):
        """
        Remove comments form text
        (Not user)
        """
        newLines = []
        lines = self.split_lines(text)
        for l in lines:
            nl = l.split('//')[0].replace('\t', ' ')
            if nl:
                newLines.append(nl)
        text = self.join_lines(newLines)
        text = re.sub(re.compile(r'/\*.*?\*/', re.DOTALL), '', text)
        return text

    def parse_block(self, i, index=0):
        """
        Parse comments
        """
        self.start = index
        state = S_CODE
        while True:
            if not i:
                return i, index
            try:
                c = i.next()
                index += 1
            except StopIteration:
                self.parse_block_content()
                return i, None
                # break
            if state == S_CODE:
                if c == '/':
                    c = i.next ()
                    index += 1
                    if c == '*':
                        com = Comment()
                        com.s = index
                        com.text += '/*'
                        state = S_MULTLINE
                        continue
                    elif c == '/':
                        com = Comment()
                        com.s = index
                        com.text += '//'
                        state = S_INLINE
                        continue
                # in code

                # search blocks
                elif c == '{': # new block
                    p = Parser(self)
                    p.code = '{'
                    i, index = p.parse_block(i, index)
                    self.code += '{block%s|%s|%s}' % (p.id, p.start, p.end)
                    self.blocks.append(p)
                elif c == '}':
                    self.code += c
                    self.end = index
                    self.parse_block_content()
                    return i, index
                else:
                    self.code += c

            elif state == S_INLINE:
                com.text += c
                if c == '\n':
                    com.e = index
                    self.comments.append(com)
                    state = S_CODE
            elif state == S_MULTLINE:
                if c == '*':
                    c = i.next ()
                    index += 1
                    if c == '/':
                        com.text += '*/\n'
                        com.e = index
                        self.comments.append(com)
                        state = S_CODE
                    else:
                        com.text += '*%s' % c
                else:
                    com.text += c
        self.parse_block_content()
        return i, index

    def parse_include(self, filename):
        """
        Parse included files
        """
        p = includes.get_include_file(filename)
        if p:
            self.var['vars'] = list(set(p.var['vars'] + self.var['vars']))
            self.var['func'] = list(set(p.var['func'] + self.var['func']))
        else:
            print 'Not found', filename

    def parse_function_variables(self, line):
        """
        Parse function variables
        """
        pat = r'(\w+)\s+(\w+)(\[.*?\])?\s?(;|\))'
        for v in re.findall(pat,line):
            self.var['vars'].append(v[1])
        self.var['vars'] = list(set(self.var['vars']))

    def parse_block_content(self):
        """
        Parse block content
        """
        # functions
        pat = r'([\w\[\]]+)\s+([\w_]+)(\(.*?\))[\n\s]*?\{block(\d+)[|\d]+\}'
        # c = re.compile(pat, re.DOTALL)
        # c = re.compile(pat)
        to_variables = self.code

        for p in re.finditer(pat, self.code):
            self.var['func'].append(p.groups()[1])
            id = int(p.groups()[3])
            for b in self.blocks:
                if b.id == id:
                    b.parse_function_variables(p.groups()[2])
            to_variables = to_variables.replace(p.group(0),'')
        self.var['func'] = list(set([x for x in self.var['func'] if not x in keywords.get_functions()+keywords.words['keywords'] ]))

        # define
        pat = r'#define\s+([\w_\d]+?)(\s+|;|\()'
        for v in re.findall(pat, to_variables):
            self.var['vars'].append(v[0])
        # variables
        # int k = 0;
        pat = r'(\w+)\s+(\w+)(\[.*?\])?\s?(;|\))'
        for v in re.findall(pat, to_variables):
            if not v[1].isdigit():
                self.var['vars'].append(v[1])
        # x = x + 3;
        pat = r'(\w+)?\s+(\w+)(\[.*?\])?\s*?(\+|\-|\/|\*)?='
        for v in re.findall(pat, to_variables):
            if not v[1].isdigit():
                self.var['vars'].append(v[1])
        # include
        # #include <math.h>
        pat = r'#include\s+<(.*?)>'
        for v in re.findall(pat, to_variables):
            self.parse_include(v)
        self.var['vars'] = list(set(self.var['vars']))


    @classmethod
    def parse(cls, text):
        '''
        Create new Block from text
        '''
        # text = text.replace('\\\n', ' ')
        it = iter(text)
        p = cls()
        p.parse_block(it)
        return p

    ################################## GET DATA

    def functions(self):
        """
        Block functions
        """
        f = self.var['func']
        if self.parent:
            f += self.parent.functions()
        return f

    def variables(self):
        """
        Block variables
        """
        v = self.var['vars']
        if self.parent:
            v += self.parent.variables()
        return v

    def get_names_at(self, pos, word=None):
        """
        Get auto completion names for position in text
        """
        for c in self.comments:
            if pos-1 > c.s and pos < c.e+1:
                return []
        for b in self.blocks:
            if pos > b.start and pos < b.end:
                return b.get_names_at(pos, word)
        if word:
            comps = self.compile_completion(dict(
                vars = list(set([x for x in self.variables() if x.lower().startswith(word.lower()) and not x == word])),
                func = list(set([x for x in self.functions() if x.lower().startswith(word.lower()) and not x == word])),
                types=[],
                keys=[]
            ), word)
            return comps
        return []

    def compile_completion(self, names, word):
        lines = []
        default = self.default_completes(word)
        for name in names['vars'] + default['vars']:
            if not name == word:
                lines.append(wordCompletion(name, word, wordCompletion.ATTRIBUTE))
        for name in default['types']:
            if not name == word:
                lines.append(wordCompletion(name, word, wordCompletion.TYPE))
        for name in names['func'] + default['func']:
            if not name == word:
                lines.append(wordCompletion(name, word, wordCompletion.FUNCTION))
        for name in default['keys']:
            if not name == word:
                lines.append(wordCompletion(name, word, wordCompletion.KEYWORD))
        return lines

    def default_completes(self, word):
        comps = dict(
            vars=[],
            func=[],
            types=[],
            keys=[]
        )
        for func in keywords.get_functions():
            if func.lower().startswith(word.lower()):
                comps['func'].append(func)
        for key in keywords.words['keywords']:
            if key.lower().startswith(word.lower()):
                comps['keys'].append(key)
        for type in keywords.words['types']:
            if type.lower().startswith(word.lower()):
                comps['types'].append(type)
        for type in keywords.words['variables']:
            if type.lower().startswith(word.lower()):
                comps['vars'].append(type)
        return comps


    def show(self, ind = 0):
        """
        Pretty print blocks tree
        """
        print ' '*ind, 'BLOCK: %s (%s-%s)' % (self.id, self.start, self.end)
        if self.var['func']:
            print ' '*ind, 'Functions:'
            print ' '*ind, '  ', ', '.join(self.var['func'])
        if self.var['vars']:
            print ' '*ind, 'Variables:'
            print ' '*ind, '  ', ', '.join(self.var['vars'])
        for b in self.blocks:
            b.show(ind+1)

    def block(self, id):
        """
        Get block by id
        """
        for b in self.blocks:
            if id == b.id:
                return b
            else:
                sub_b = b.block(id)
                if sub_b:
                    return sub_b

    @classmethod
    def parse_help_line(cls, text):
        if not text:
            return
        it = iter(reversed(text))
        con = pos = i = 0
        while True:
            try:
                c = it.next()
                i += 1
            except StopIteration:
                return
            if c == '(':
                if con == 0:
                    pos = i
                    break
                con -= 1
            elif c == ')':
                con += 1

        pos = len(text)-pos
        f = re.findall(r'([\w\d_]+)[\s]*\($', text[:pos+1])
        if f:
            func = f[0]
            return func
        else:
            return cls.parse_help_line(text[:pos])

class AttributesParser(object):
    def __init__(self, word, parm):
        self.word = word or ''
        self.attrs = []
        if parm:
            node = parm.node()
            try:
                node_attrs = sorted([x.name() for x in node.geometry().pointAttribs() + node.geometry().primAttribs() + node.geometry().vertexAttribs() +node.geometry().globalAttribs() if not x.name() in ['varmap', 'Pw', 'P']], key=lambda x:x.lower())
                if word:
                    node_attrs = [x for x in node_attrs if x.startswith(word)]
                self.attrs += node_attrs
            except:
                pass
        if word:
            self.attrs += sorted(list(set([a for a in keywords.get_attributes() if a.lower().startswith(word.lower())])), key=lambda x:x.lower())
        else:
            self.attrs += sorted(list(set(keywords.get_attributes())), key=lambda x:x.lower())

    def get_names(self):
        names = []
        for a in self.attrs:
            names.append(wordCompletion(a, self.word, wordCompletion.ATTRIBUTE))
        return names


class wordCompletion(object):
    ATTRIBUTE = 0
    FUNCTION = 1
    DEFINITION = 3
    TYPE = 4
    KEYWORD = 5
    VARIABLE = 6
    def __init__(self, name, word, type):
        self.type = type
        self.word = word
        self.complete = name[len(word):]
        self.name = name

    def __repr__(self):
        return self.word + '| |' + self.complete



