# http://www.sidefx.com/docs/houdini14.0/vex/vop_structs
# http://www.sidefx.com/docs/houdini14.0/vex/lang#structs
#
# << а, ну да, типа:
# int nums[] = { 0, 1, 2, 3, 4, 5 };
#
#


class Comment():
    def __init__(self):
        self.text = ''
        self.s = 0  # start
        self.e = 0  # end

text = open('C:/cg/Houdini/14.0.395/houdini/vex/include/pyro_math.h').read()
import time
import sys
sys.path.append(r'D:\Dropbox\Dropbox\pw_pipeline\pw_pipeline\assets\houdini\python\VEX\pw_VEX_Editor\autocomplete')
from autocomplete import vex_parser
reload(vex_parser)
p = vex_parser.Parser.parse(text)
t1 = time.time()
vex_parser.includes.includes['pyro_utils.h'].show()
print time.time() - t1

p.show()

text = open('C:/cg/Houdini/14.0.395/houdini/vex/include/math.h').read()
p = vex_parser.Parser.parse(text)
