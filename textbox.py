import tkinter as tk
from tkinter.scrolledtext import ScrolledText


class App(tk.Tk):
    def __init__(self, title='', width=640, height=480, user_callback=None, users_callback_args=None, rate=1.0):
        super().__init__()
        self.title(title)
        self.geometry(f'{width}x{height}')
        self.scrolled_text = ScrolledText(self)
        self.scrolled_text.pack(padx=5, pady=5, fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.user_callback = user_callback
        self.users_callback_args = self
        self.rate = rate
        if self.rate:
            self.after(int(1000.0 / self.rate), self.callback)
        else:
            self.after(0, self.callback)

    def insert(self, text, line=1, column=0):
        self.scrolled_text.insert(f'{line}.{column}', text)

    def clear(self):
        self.scrolled_text.delete('1.0', tk.END)

    def callback(self):
        self.user_callback(self, self.users_callback_args)
        if self.rate:
            self.after(int(1000.0 / self.rate), self.callback)


text_count = 0


def my_callback(widget, args):
    global text_count
    widget.insert(f'new text {text_count}\n')
    text_count = text_count + 1
    if text_count > 20:
        widget.clear()
        text_count = 0


if __name__ == "__main__":
    app = App(title='title', width=640, height=480, user_callback=my_callback, rate=0)
    app.mainloop()
