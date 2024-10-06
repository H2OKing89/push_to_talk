# utils/gui_utils.py

import tkinter as tk

class CreateToolTip:
    """
    Create a tooltip for a given widget with enhanced customization.
    """
    def __init__(self, widget, text='widget info', bg="#ffffe0", fg="black", wraplength=300):
        self.waittime = 500     # milliseconds
        self.wraplength = wraplength   # pixels
        self.widget = widget
        self.text = text
        self.bg = bg
        self.fg = fg
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def showtip(self, event=None):
        """Display text in tooltip window"""
        x, y, cx, cy = self.widget.bbox("insert") if self.widget.bbox("insert") else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)  # removes all window managers
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            self.tw, text=self.text, justify='left',
            background=self.bg, foreground=self.fg, relief='solid', borderwidth=1,
            wraplength=self.wraplength,
            font=("tahoma", "8", "normal")
        )
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()

def create_tooltip(widget, text, bg="#ffffe0", fg="black", wraplength=300):
    """Utility function to create tooltips with enhanced customization."""
    CreateToolTip(widget, text, bg, fg, wraplength)
