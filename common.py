import sys
from os.path import join, abspath, dirname, normpath

# from main import __file__ as __mainfile__

BASE_RESOURCE_PATH = None
if getattr(sys, 'frozen', False): # PyInstaller
    BASE_RESOURCE_PATH = sys._MEIPASS # type: ignore
elif '__compiled__' in globals(): # Nuitka
    BASE_RESOURCE_PATH = dirname(__file__)
else:
    BASE_RESOURCE_PATH = abspath('.')
assert BASE_RESOURCE_PATH is not None

def resource_path(*args):
    return normpath(join(BASE_RESOURCE_PATH, *args))