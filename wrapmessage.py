from __future__ import print_function

import tkinter as tk
import tkinter.ttk as ttk

from tkinter.messagebox import showinfo

from tkinter import Message

class WrapMessage(Message):
    padding = 10

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Configure>", self._adjustWidth)
        
    def configure(self, cnf={}, **kw):
        # showinfo("Input config", '{} {}'.format(cnf, kw))
        
        key = 'padding'
        if key in cnf:
            self.padding = int(cnf[key])
            del cnf[key]
        if key in kw:
            self.padding = int(kw[key])
            del kw[key]
            
        # showinfo("Output config", '{} {}'.format(cnf, kw))
        
        super().configure(cnf, **kw)
        
    config = configure
    
    def cget(self, key):
        option = 'padding'
        if key == option:
            return self.padding

        return super().cget(key)
    
    def _adjustWidth(self, event):
        print(self.padding)
        event.widget.configure(width=event.width-self.padding)
        
        
if __name__ == '__main__':
    root = tk.Tk()
    msg = WrapMessage(root)
    msg.configure(padding=40, text="This is a WrapMessage.")
    msg.pack(fill='both', expand=True)
    root.mainloop()