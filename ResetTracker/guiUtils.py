from tkinter import *
from PIL import ImageTk, Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import io

from graphs import *


# gui
class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()


# gui
class PlotFrame(tk.Frame):
    def __init__(self, parent, fig=None, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.fig = fig
        self.canvas = None
        self.plot_widget = None
        self.grid(row=0, column=0)
        if fig is not None:
            self.create_plot_widget()

    def create_plot_widget(self):
        if isinstance(self.fig, plt.Figure):
            self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
            self.canvas.draw()

        elif isinstance(self.fig, sns.matrix.ClusterGrid):
            self.canvas = FigureCanvasTkAgg(self.fig.fig, master=self)
            self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
            self.canvas.draw()

        elif isinstance(self.fig, go.Figure):
            img_bytes = self.fig.to_image(format='png')
            img = Image.open(io.BytesIO(img_bytes))
            img_tk = ImageTk.PhotoImage(img)
            self.plot_widget = tk.Label(self, image=img_tk)
            self.plot_widget.image = img_tk
            self.plot_widget.grid(column=0, row=0)

        else:
            raise ValueError('Unsupported figure type')


# gui
class TooltipObject:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

    def show_tip(self):
        if self.tip_window or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox('insert')
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


# gui
class Tooltip:
    @classmethod
    def createToolTip(cls, widget, text):
        tooltip = TooltipObject(widget, text)
        widget.bind('<Enter>', lambda _: tooltip.show_tip())
        widget.bind('<Leave>', lambda _: tooltip.hide_tip())


# gui
class ScrollableTextFrame(tk.Frame):
    def __init__(self, master, header_text='', **kwargs):
        super().__init__(master, **kwargs)

        # Create header label
        self.header_label = tk.Label(self, text=header_text, font=('TkDefaultFont', 14, 'bold'))
        self.header_label.pack(side=tk.TOP, fill=tk.X)

        # Create a vertical scrollbar
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a horizontal scrollbar
        hscrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a text widget with scrollbars
        self.text = tk.Text(self, wrap=tk.NONE, xscrollcommand=hscrollbar.set, yscrollcommand=vscrollbar.set,
                            state='disabled')
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure the scrollbars to scroll the text widget
        vscrollbar.config(command=self.text.yview)
        hscrollbar.config(command=self.text.xview)
        self.text.config(yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)

    def set_header(self, header_text):
        self.header_label.config(text=header_text)

    def set_text(self, text):
        self.text.config(state='normal')
        self.text.delete('1.0', tk.END)
        self.text.insert(tk.END, text)
        self.text.config(state='disabled')