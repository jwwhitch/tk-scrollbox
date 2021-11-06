import argparse
import os
import re
import shutil
import tkinter as tk
from tkinter import Menu, filedialog


KEYWORDS = {
    'blue': (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6}',),
    'yellow': (r'-WARNING-',),
    'red': (r'-ERROR-',),
    'green': (r'-INFO-',)
}
IGNORE_CASE = 0


class App(tk.Tk):
    def __init__(self, title='', width=640, height=480, rate=1.0,
                 user_callback=None, user_callback_args=None):
        super().__init__()
        self.window_title = title
        self.user_callback = user_callback
        self.user_callback_args = user_callback_args
        self.__set_title(self.window_title)
        self.geometry(f'{width}x{height}')
        self.__create_menu()
        self.main_text = tk.Text(self, bg="black", fg="white", wrap=tk.NONE)
        self.main_text_xsb = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.main_text.xview)
        self.main_text_ysb = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.main_text.yview)
        self.main_text.configure(yscrollcommand=self.main_text_ysb.set, xscrollcommand=self.main_text_xsb.set)
        self.main_text_xsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.main_text_ysb.pack(side=tk.RIGHT, fill=tk.Y)
        self.main_text.pack(padx=5, pady=5, fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.rate = rate
        if self.rate:
            self.after(int(1000.0 / self.rate), self.callback)
        else:
            self.after(0, self.callback)

    def __set_title(self, title):
        if self.user_callback_args:
            title = f"{title}-{os.path.abspath(self.user_callback_args)}"
        self.title(title)

    def __create_menu(self):
        menu_bar = Menu(self)
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.__file_open)
        file_menu.add_command(label="Save as...", command=self.__file_save_as)
        file_menu.add_command(label="Close", command=self.__file_close)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu_bar)

    def __file_open(self):
        filename = filedialog.askopenfilename(
            filetypes=(("text files", "*.txt"), ("log files", "*.log"), ("all files", "*.*")))
        if filename:
            self.user_callback_args = filename
            self.__set_title(self.window_title)

    def __file_close(self):
        self.clear()
        self.user_callback_args = None
        self.__set_title(self.window_title)

    def __file_save_as(self):
        filename = filedialog.asksaveasfilename(
            filetypes=(("text files", "*.txt"), ("log files", "*.log"), ("all files", "*.*")))
        if filename and self.user_callback_args:
            shutil.copy2(self.user_callback_args, filename)

    @staticmethod
    def __find_keywords(text_string):
        line_number = 0
        keyword_locations = []
        for line in text_string.split('\n'):
            line_number += 1
            for color, keywords in KEYWORDS.items():
                for keyword in keywords:
                    for match in re.finditer(keyword, line, IGNORE_CASE):
                        keyword_locations.append(
                            (color,
                             f"{line_number}.{match.start()}",
                             f"{line_number}.{match.end()}"))
        return keyword_locations

    def __decorate_text(self, text_string):
        for keyword_location in self.__find_keywords(text_string):
            self.main_text.tag_add(keyword_location[0], keyword_location[1], keyword_location[2])
            self.main_text.tag_config(keyword_location[0], foreground=keyword_location[0])

    def insert(self, text, line=1, column=0):
        self.main_text.config(state=tk.NORMAL)
        self.main_text.insert(f'{line}.{column}', text)
        self.main_text.config(state=tk.DISABLED)
        self.main_text.yview_moveto(0.0)

    def append(self, text):
        self.main_text.config(state=tk.NORMAL)
        self.main_text.insert(tk.END, text)
        self.__decorate_text(text)
        self.main_text.config(state=tk.DISABLED)
        self.main_text.yview_moveto(1.0)

    def clear(self):
        self.main_text.config(state=tk.NORMAL)
        self.main_text.delete('1.0', tk.END)
        self.main_text.config(state=tk.DISABLED)

    def callback(self):
        self.user_callback((self, self.user_callback_args))
        if self.rate:
            self.after(int(1000.0 / self.rate), self.callback)


class WindowUpdate:

    stat_info = None

    @staticmethod
    def window_update(args):
        widget, file_name = args
        try:
            update = os.stat(file_name)
            if not WindowUpdate.stat_info or WindowUpdate.stat_info.st_mtime != update.st_mtime:
                with open(file_name, 'r') as file_stream:
                    contents = file_stream.read()
                    widget.clear()
                    widget.append(contents)
            WindowUpdate.stat_info = update
        except (TypeError, FileNotFoundError):
            WindowUpdate.stat_info = None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Display the contents of a file.')
    parser.add_argument('file', help='name of the file to open')
    program_args = parser.parse_args()
    app = App(title='AppTail', width=640, height=480, rate=1.0,
              user_callback=WindowUpdate.window_update, user_callback_args=program_args.file)
    app.mainloop()
