import logging
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from datetime import datetime


class App(tk.Tk):
    def __init__(self, icon='icon.ico', title='', width=640, height=480, user_callback=None, user_callback_args=None, rate=1.0):
        super().__init__()
        self.title(title)
        self.iconbitmap(default=icon)
        self.geometry(f'{width}x{height}')
        self.scrolled_text = ScrolledText(self)
        self.scrolled_text.pack(padx=5, pady=5, fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.user_callback = user_callback
        self.users_callback_args = (self, user_callback_args)
        self.rate = rate
        if self.rate:
            self.after(int(1000.0 / self.rate), self.callback)
        else:
            self.after(0, self.callback)

    def insert(self, text, line=1, column=0):
        self.scrolled_text.config(state=tk.NORMAL)
        self.scrolled_text.insert(f'{line}.{column}', text)
        self.scrolled_text.config(state=tk.DISABLED)
        self.scrolled_text.yview_moveto(0.0)

    def append(self, text):
        self.scrolled_text.config(state=tk.NORMAL)
        self.scrolled_text.insert(tk.END, text)
        self.scrolled_text.config(state=tk.DISABLED)
        self.scrolled_text.yview_moveto(1.0)

    def clear(self):
        self.scrolled_text.config(state=tk.NORMAL)
        self.scrolled_text.delete('1.0', tk.END)
        self.scrolled_text.config(state=tk.DISABLED)

    def callback(self):
        self.user_callback(self.users_callback_args)
        if self.rate:
            self.after(int(1000.0 / self.rate), self.callback)


event_count = 0


def my_callback(args):
    global event_count
    log_string = f"{datetime.utcnow()} UTC-logged event {event_count}"
    args[0].append(f"{log_string}\n")
    logging.info(log_string)
    event_count += 1


if __name__ == "__main__":
    logging.basicConfig(filename='MyLog.txt', level=logging.DEBUG)
    app = App(icon='icon.ico', title='title', width=640, height=480, user_callback=my_callback,
              user_callback_args=None, rate=1.0)
    app.mainloop()
