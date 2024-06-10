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


try:
    from pygubu.api.v1 import (
        BuilderObject,
        register_widget,
    )
except ImportError as e:
    from pygubu import BuilderObject, register_widget # type: ignore

from wrapmessage import WrapMessage
from checkablelabelframe import CheckableLabelFrame

class WrapMessageBuilder(BuilderObject): # type: ignore
    class_ = WrapMessage

    OPTIONS_STANDARD = ('anchor', 'background', 'borderwidth', 'cursor', 'font',
                        'foreground', 'highlightbackground', 'highlightcolor',
                        'highlightthickness', 'padx', 'pady', 'relief', 'takefocus',
                        'text', 'textvariable')
    OPTIONS_SPECIFIC =  ('aspect', 'justify', 'width', 'padding')
    properties = OPTIONS_STANDARD + OPTIONS_SPECIFIC

class CheckableLabelFrameBuilder(BuilderObject): # type: ignore
    class_ = CheckableLabelFrame
    container = True

    OPTIONS_STANDARD = ('cursor', 'takefocus', 'style')
    OPTIONS_SPECIFIC = ('borderwidth', 'relief', 'padding', 'height', 'width', 'labelanchor', 'text', 'underline', 'variable', 'command')
    
    properties = OPTIONS_STANDARD + OPTIONS_SPECIFIC

register_widget(
    'customwidgets.WrapMessage', WrapMessageBuilder, 'WrapMessage', ('tk', 'Custom'))
register_widget(
    'customwidgets.CheckableLabelFrame', CheckableLabelFrameBuilder,
    'CheckableLabelFrame', ('ttk', 'Custom'))