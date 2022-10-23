import sys
from os.path import join, abspath

def resource_path(*args):
    if getattr(sys, 'frozen', False):
        r = join(sys._MEIPASS, *args)  # type: ignore
    else:
        r = join(abspath('.'), *args)
    return r