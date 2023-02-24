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


from __future__ import print_function

import tkinter as tk
import traceback
from tkinter import Button, Checkbutton, IntVar
from tkinter.messagebox import showinfo
from tkinter.ttk import LabelFrame
from tkinter.ttk import Widget as TtkWidget
from typing import Any


class CheckableLabelFrame(LabelFrame):
    """LabelFrame widget with a tkinter.Checkbutton as the label."""
    def __init__(self, master=None, **kwargs):
        self.variable: IntVar = IntVar()
        self.callback_update_name: str = ''
        self.command = None

        super().__init__(master, **kwargs)

        self.checkbutton = Checkbutton(self, text=self["text"], variable=self.variable, command=self._handler)
        self.configure(labelwidget=self.checkbutton)

    def configure(self, cnf = None, **kw):
        if cnf is None:
            cnf = {}
        def pop_config(key) -> Any:
            nonlocal kw
            value = None
            if key in cnf:
                value = cnf[key]
                del cnf[key]
            if key in kw:
                value = kw[key]
                del kw[key]
            return value

        text: str = pop_config('text')
        variable: IntVar = pop_config('variable')
        command = pop_config('command')

        if text:
            self.checkbutton["text"] = text

        if variable:
            if self.variable and self.callback_update_name:
                self.variable.trace_remove('write', self.callback_update_name) #type: ignore
            variable.set(1)
            self.checkbutton["variable"] = variable
            self.callback_update_name = variable.trace_add('write', self.updateState)
            self.variable = variable

        if command:
            self.command = command


        super().configure(cnf, **kw)

    config = configure

    def cget(self, key):
        if key == 'variable':
            return self.variable
        if key == 'command':
            return self.command
        if key == 'text':
            return self.checkbutton["text"]

        return super().cget(key)

    def updateState(self, *args) -> None:
        """Update children' state according to its 'variable' key's value.
            The children' original states won't be preserved."""
        if self.variable:
            state = 'normal' if self.variable.get() else 'disable'
            ttkState = ('!disabled' if self.variable.get() else 'disabled',)
            stack = list(self.winfo_children())
            while stack:
                descendent = stack.pop()
                if descendent == self.checkbutton:
                    continue
                stack.extend(descendent.winfo_children())
                try:
                    wtype = descendent.winfo_class()
                    if wtype not in ('Frame', 'Labelframe'):
                        if isinstance(descendent, TtkWidget):
                            descendent.state(ttkState)
                        else:
                            descendent["state"] = state
                except tk.TclError:
                    print(traceback.format_exc())


    def _handler(self) -> None:
        if self.command:
            self.command()


if __name__ == '__main__':
    root = tk.Tk()
    option = tk.IntVar()
    frame = CheckableLabelFrame(root)
    frame.configure(text="My option group", variable=option)

    btn = Button(frame, text ="CheckableLabelFrame")
    btn.pack()

    frame.pack(fill='both', expand=True)

    option.set(0)

    root.mainloop()