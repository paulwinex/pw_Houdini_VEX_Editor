import os

root = os.path.dirname(__file__)

def join(*args):
    return os.path.join(*args).replace('\\','/')

# icons = {os.path.splitext(x)[0]:join(root,x) for x in os.listdir(root) if os.path.splitext(x)[-1] == '.png'}
icons = {}
for x in os.listdir(root):
    if os.path.splitext(x)[-1] == '.png':
        icons[os.path.splitext(x)[0]] = join(root,x)
