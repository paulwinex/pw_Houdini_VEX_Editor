import os, re

return_types = ['float','int','void','struct','vector','vector4','surface','pop','chop','cop2','cvex','displacement','fog','image3d','light','shadow','sop']
var_types = ["float",
             "vector2",
             "vector",
             "vector4",
             "int",
             "matrix2",
             "matrix3",
             "matrix",
             "string"]

class VEX_Parser(object):
    def __init__(self, text):
        self.text = text

    def parse_code(self):
        self.script = dict(
            functions = [],
            variables = [],
            defined=[]
        )
        # get lines
        lines = self.text.split('\n')
        # remove comments
        newLines = []
        for l in lines:
            nl = l.split('//')[0].replace('\t', ' ')
            if nl:
                newLines.append(nl)
        text = ''.join(newLines)
        text = re.sub(re.compile(r'/\*.*?\*/', re.DOTALL), '', text)

        # collapse blocks
        excluded = ''
        blocks = {}
        i = 0
        b=0

        while i < len(text):
            # new block founded
            if text[i] == '{':

               blocks[b] = ''
               blocks[b] += text[i]
               pair = 1
               # search to end of block
               while pair > 0 and i < len(text):
                   i += 1
                   if text[i] == '{': pair += 1
                   elif text[i] == '}': pair -= 1
                   blocks[b] += text[i]
               # if function founded
               # print blocks[b]
               if not re.findall(r'^\{((.+?|\s),?)+\}', blocks[b].strip()):
                   excluded += '{block%s}' % b
                   b += 1
               else:
                   # back to code
                   excluded += blocks[b]
               # end of code
               if pair > 0:
                   pass
                   # print 'From editor'
            else:
               excluded += text[i]
            i += 1
        # search functions

        func_pat = r'[\s]*('+'|'.join(return_types)+r')[\s]+([\w]+)\([\w\s\d,;\[\]]+\)\s+\{block\d+\}'
        to_replace = []
        for s in re.finditer(func_pat, excluded):
            self.script['functions'].append( s.group(2) )
            to_replace.append(s.group(0))
        for t in to_replace:
            excluded = excluded.replace(t, '', 1)

        # search variables

        lines = excluded.split('\n')
        def_pat = r'#define\s+([\w]+)'
        newLines = []
        for line in lines:
            if line:
                v = re.findall(def_pat, line.strip())
                if v:
                    self.script['defined'] += v
                    # line = line.replace(v.group(0),'').strip()
                if line:
                    newLines.append(line)

        newLines2 = []
        pat = r'('+'|'.join(var_types)+r')\s+([\w, ]+).*;'
        for l in newLines:
            v = re.match(pat, l.strip())
            if v:
                self.script['variables'].append(v.group(2))
                l = l.replace(v.group(0),'')
            newLines2.append(l)

        newLines = []
        pat = r'^[\s]*([\w,\s]+)\s*='
        for l in newLines2:
            v = re.match(pat, l)
            if v:
                vars = [x[0].strip() for x in [x.split(',') for x in v.group(1).split()] if x[0].strip() and not x[0].strip() in var_types]
                self.script['variables'] += vars

        # included

        self.script['functions'] = list(set(self.script['functions']))
        self.script['variables'] = list(set(self.script['variables']))
        self.script['defined'] = list(set(self.script['defined']))

        return self.script

