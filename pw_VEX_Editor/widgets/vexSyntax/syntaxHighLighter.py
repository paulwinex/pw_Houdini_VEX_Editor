from PySide.QtCore import *
from PySide.QtGui import *
import re
import design
reload(design)
import keywords
reload(keywords)

class VEXHighlighterClass (QSyntaxHighlighter):
    def __init__(self, document, colors=None, extraSyntax=None):
        QSyntaxHighlighter.__init__(self, document)

        if colors:
            self.colors = colors
        else:
            self.colors = design.getColors()

        # Multi line comments
        self.multi_line = (QRegExp("/\*"),QRegExp("\*/"), 1, self.getStyle(self.colors['code']['comment']))

        rules = []

        # Operators
        ops = '('+ '|'.join(keywords.syntax['operators']) + ')'
        rules += [(ops, 0, self.getStyle(self.colors['code']['operator']))]

        # Defined
        # rules += [(r"#(ifndef|define)\s+(\w+)", 2, self.getStyle(self.colors['code']['includes']))]
        # rules += [(r"(#\w+\s|!?defined)\s?([\w\(\)]+)", 2, self.getStyle(self.colors['code']['includes']))]
        # rules += [(r'''(#if\s+|#)!?\w+\s(.+)\s''', 2, self.getStyle(self.colors['code']['includes']))]

        # types
        rules += [("\\b%s\\b" % b, 0, self.getStyle(self.colors['code']['type']))
            for b in keywords.syntax['types']]

        #Braces
        rules += [(r'[\{\}\(\)\[\]]', 0, self.getStyle(self.colors['code']['brace']))]

        # Digits
        rules += [(r"\b[\d]+\w?\b", 0, self.getStyle(self.colors['code']['digits']))]


        # variable
        rules += [(r"\B\$[\w\d]+", 0, self.getStyle(self.colors['code']['variable'], True))]

        # Includes
        rules += [(r"#include\s+(<.*>)", 1, self.getStyle(self.colors['code']['includes']))]

        # Directive
        rules += [('#?\\b!?%s\\b' % w, 0, self.getStyle(self.colors['code']['directive'], True))
            for w in keywords.syntax['directive']+keywords.syntax['ifdirective']]
        # rules += [(r'(#if\s+|#)!?\w+' , 0, self.getStyle(self.colors['code']['directive'], True))]
        # Pragma
        rules += [('#pragma\s+(%s)' % w, 0, self.getStyle(self.colors['code']['directive'], True))
            for w in keywords.syntax['pragma']]
        # rules += [(r'(#if\s+|#)!?\w+' , 0, self.getStyle(self.colors['code']['directive'], True))]

        # Methods
        rules += [("\\b[A-Za-z0-9_]+\s*(?=\\()", 0, self.getStyle(self.colors['code']['methods'], True))]

        # Keywords
        rules += [(r'(^|[^#])\b(%s)\b' % w, 2, self.getStyle(self.colors['code']['keywords'], True))
            for w in keywords.syntax['keywords']]

        # attributes
        rules += [(r"(v4|v|s|i|f|u|p|2|3|4)?(\[\])?@[\w.]+", 0, self.getStyle(self.colors['code']['attribute']))]

        # Double-quoted string
        rules += [(r'[ru]?"[^"\\]*(\\.[^"\\]*)*"', 0, self.getStyle(self.colors['code']['string']))]

        # Single-quoted string
        rules += [(r"[ru]?'[^'\\]*(\\.[^'\\]*)*'", 0, self.getStyle(self.colors['code']['string']))]

        # Comment
        rules += [(r'//([.*]+|[^//]*)', 0, self.getStyle(self.colors['code']['comment']))]

        #whitespace
        rules += [(r'\s', 0, self.getStyle(self.colors['code']['whitespace']))]


        # extra
        if extraSyntax:
            rules += extraSyntax
        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt) for (pat, index, fmt) in rules]
        # self.rehighlight()

    @classmethod
    def getStyle(self, color, bold=False):
        brush = QBrush( QColor(*color))
        f = QTextCharFormat()
        if bold:
            f.setFontWeight( QFont.Bold )
        f.setForeground( brush )
        return f

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        defFormat = self.getStyle(self.colors['code']['default'])
        self.setFormat(0, len(text), defFormat)

        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)
            # print expression, index
            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


        strings = re.findall(r'(".*?")|(\'.*?\')', text)
        if '//' in text:
            copy = text
            if strings:
                pat = []
                for s in strings:
                    for match in s:
                        if match:
                            pat.append(match)
                for s in pat:
                    copy = copy.replace(s, '_'*len(s))
            if '//' in copy:
                index = copy.index('//')
                length = len(copy) - index
                self.setFormat(index, length, self.getStyle(self.colors['code']['comment']))

        self.setCurrentBlockState(0)

        # Do multi-line strings
        self.match_multiline(text, *self.multi_line)


    def match_multiline(self, text, delimiter_start, delimer_end, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished. """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter_start.indexIn(text)
            # Move past this match
            add = delimiter_start.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimer_end.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimer_end.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match

            start = delimiter_start.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False


