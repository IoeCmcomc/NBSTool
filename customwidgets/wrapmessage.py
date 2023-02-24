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
import tkinter.ttk as ttk

from tkinter.messagebox import showinfo

from tkinter import Message

class WrapMessage(Message):
    padding = 10

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<Configure>", self._adjustWidth)

    def configure(self, cnf = None, **kw):
        if cnf is None:
            cnf = {}
        key = 'padding'
        if key in cnf:
            self.padding = int(cnf[key])
            del cnf[key]
        if key in kw:
            self.padding = int(kw[key])
            del kw[key]

        super().configure(cnf, **kw)

    config = configure

    def cget(self, key):
        option = 'padding'
        if key == option:
            return self.padding

        return super().cget(key)

    def _adjustWidth(self, event):
        event.widget.configure(width=event.width-self.padding)


if __name__ == '__main__':
    root = tk.Tk()
    msg = WrapMessage(root)
    msg.configure(padding=40, text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus gravida libero ac commodo molestie. Donec iaculis velit sem, consequat bibendum libero cursus ut. Nulla ullamcorper placerat libero malesuada dignissim. Aliquam et hendrerit erat, non aliquet mi. Ut eu urna ligula. Donec mattis sollicitudin purus. Proin tellus libero, interdum porta mauris ac, interdum gravida sapien. Proin maximus purus ut dui ultrices, eget blandit est consectetur.")
    msg.pack(fill='both', expand=True)
    root.mainloop()