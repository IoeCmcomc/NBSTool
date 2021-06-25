# This file is a part of:
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#  ███▄▄▄▄   ▀█████████▄     ▄████████     ███      ▄██████▄   ▄██████▄   ▄█
#  ███▀▀▀██▄   ███    ███   ███    ███ ▀█████████▄ ███    ███ ███    ███ ███
#  ███   ███   ███    ███   ███    █▀     ▀███▀▀██ ███    ███ ███    ███ ███
#  ███   ███  ▄███▄▄▄██▀    ███            ███   ▀ ███    ███ ███    ███ ███
#  ███   ███ ▀▀███▀▀▀██▄  ▀███████████     ███     ███    ███ ███    ███ ███
#  ███   ███   ███    ██▄          ███     ███     ███    ███ ███    ███ ███
#  ███   ███   ███    ███    ▄█    ███     ███     ███    ███ ███    ███ ███▌    ▄
#   ▀█   █▀  ▄█████████▀   ▄████████▀     ▄████▀    ▀██████▀   ▀██████▀  █████▄▄██
# __________________________________________________________________________________
# NBSTool is a tool to work with .nbs (Note Block Studio) files.
# Author: IoeCmcomc (https://github.com/IoeCmcomc)
# Programming language: Python
# License: MIT license
# Source codes are hosted on: GitHub (https://github.com/IoeCmcomc/NBSTool)
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾


print(f'{__name__}')

if __name__ == '__init__': # Pygubu import call
    from wrapmessage import WrapMessage
else: # Normal import call
    from .wrapmessage import WrapMessage
from pygubu import BuilderObject, register_widget

class WrapMessageBuilder(BuilderObject):
    class_ = WrapMessage

    OPTIONS_STANDARD = ('anchor', 'background', 'borderwidth', 'cursor', 'font',
                        'foreground', 'highlightbackground', 'highlightcolor',
                        'highlightthickness', 'padx', 'pady', 'relief', 'takefocus',
                        'text', 'textvariable')
    OPTIONS_SPECIFIC =  ('aspect', 'justify', 'width', 'padding')
    properties = OPTIONS_STANDARD + OPTIONS_SPECIFIC

register_widget('customwidgets.wrapmessage', WrapMessageBuilder,
                'WrapMessage', ('tk', 'Custom'))

