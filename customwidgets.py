from pygubu import BuilderObject, register_widget
from wrapmessage import WrapMessage

print(__name__)

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

