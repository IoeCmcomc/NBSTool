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
    from checkablelabelframe import CheckableLabelFrame
else: # Normal import call
    from .wrapmessage import WrapMessage
    from .checkablelabelframe import CheckableLabelFrame

from pygubu import BuilderObject, register_widget

class WrapMessageBuilder(BuilderObject):
    class_ = WrapMessage

    OPTIONS_STANDARD = ('anchor', 'background', 'borderwidth', 'cursor', 'font',
                        'foreground', 'highlightbackground', 'highlightcolor',
                        'highlightthickness', 'padx', 'pady', 'relief', 'takefocus',
                        'text', 'textvariable')
    OPTIONS_SPECIFIC =  ('aspect', 'justify', 'width', 'padding')
    properties = OPTIONS_STANDARD + OPTIONS_SPECIFIC

class CheckableLabelFrameBuilder(BuilderObject):
    class_ = CheckableLabelFrame
    container = True

    OPTIONS_STANDARD = ('cursor', 'takefocus', 'style')
    OPTIONS_SPECIFIC = ('borderwidth', 'relief', 'padding', 'height', 'width', 'labelanchor', 'text', 'underline', 'variable', 'command')
    
    properties = OPTIONS_STANDARD + OPTIONS_SPECIFIC

register_widget('customwidgets.wrapmessage', WrapMessageBuilder,
                'WrapMessage', ('tk', 'Custom'))
register_widget('customwidgets.checkablelabelframe', CheckableLabelFrameBuilder,
                'CheckableLabelFrame', ('ttk', 'Custom'))