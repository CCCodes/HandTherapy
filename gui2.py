import threading
import time
import ttk
from Tkinter import *
from PIL import Image, ImageTk
import os


HEAD = ("Arial", 16)
NOTEBOOK_COLOR = 'white'
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
NOTEBOOK_WIDTH = 430
NOTEBOOK_HEIGHT = 300

grab_str = 0
gui_goal = ""


class Window(Tk):

    def __init__(self, title, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.wm_resizable(0, 0)
        self.title(title)
        # self.wm_iconbitmap("images\doublehelix.ico")
        self.messages = ["Start a new process, convert a GEO text file to "
                         "Excel, or play with settings.",  # File
                         "Edit the main form or reset both forms.",  # Edit
                         "Toggle the status bar.",  # View
                         "Stop to stop running program then exit for quick "
                         "exit.",
                         "Plot a word cloud of an output file based on the "
                         "number of citations from PubMed.",  # Graph
                         "Edit the advanced menu."]  # Advanced
        self.bg_color = 'powder blue'

        self.container = Frame(self)
        self.container.pack(side='top', fill='both', expand=True)

        # sub_container for options bar
        self.sub_container = Frame(self.container)
        self.sub_container.pack_propagate(0)
        self.sub_container.pack()

        self.grab_var = StringVar()
        self.grab_var.set("GRAB_VAR")
        self.grab_strength = Label(self.sub_container, textvariable=self.grab_var)
        self.grab_strength.grid(row=0, pady=10)

        self.grab_num = StringVar()
        self.grab_num.set("GRAB_NUM")
        self.grab_num_lab = Label(self.sub_container, textvariable=self.grab_num)
        self.grab_num_lab.grid(row=1, pady=10)

        self.pb_space = Frame(self.container, {'height': 50,
                                               'width': 500})

        self.set_time_lab = Label(self.pb_space, text="Set interval")
        self.set_time_lab.pack()

        self.session_length = StringVar()
        self.set_time = Entry(self.pb_space, textvariable=self.session_length)
        self.session_length.set(30)
        self.set_time.pack()

        self.start_btn = Button(self.pb_space, text="Start", command=self.starting)
        self.start_btn.pack()

        self.time = IntVar()
        self.time.set(0)
        self.timer = Label(self.pb_space, textvariable=self.time)
        self.timer.pack()

        # pady 2nd param also controls status bar placement
        # if the window was resizable it would be placed incorrectly
        self.pb_space.pack(pady=10)

        self.status_bar = StatusBar(self.container)
        self.status_bar.pack(side="bottom", fill=X, expand=True, anchor='s')
        self.status_bar.set("Ready")

        self.goal = ""
        self.session = 0
        self.start = 0

        #self.main_frame = Frame(self.container, bg="white")

        #self.main_frame.pack(expand=True)

    def update_grab(self, num):
        if self.goal == "":
            self.grab_var.set("Welcome to HandTherapy Helper!")
            self.grab_num.set("Press start to begin")
        elif num == -1:  # goal is valid but no hand input
            self.grab_num.set("Center your hand!")
            return
        else:
            self.time.set(int(time.time() - self.start))
        if self.goal == "open":
            self.grab_var.set("Open your hand for %s seconds" % self.session_length.get())
            if num == 0:
                self.grab_num.set("Good job!")
            else:
                self.grab_num.set("Try harder!")
        elif self.goal == "close":
            self.grab_var.set("Close your hand for %s seconds" % self.session_length.get())
            if num == 1:
                self.grab_num.set("Good job!")
            else:
                self.grab_num.set("Try harder!")
        elif self.goal == "claw":
            self.grab_var.set("Hold between open and closed for %s seconds" % self.session_length.get())
            if .3 < num < .8:
                self.grab_num.set("Good job!")
            elif num <= .3:
                self.grab_num.set("Close your hand a bit more!")
            else:
                self.grab_num.set("Open your hand a bit more!")

    # def grab_forever(self):
    #     while True:
    #         self.after(500, self.update_grab())

    def status_bar_update(self):
        pass

    def complete(self):
        pass

    def reset(self):
        pass

    def starting(self):
        self.goal = "open"
        thread2 = threading.Thread(target=self.goal_time)
        thread2.start()

    def goal_time(self):
        self.session += 1
        self.start = time.time()
        self.goal = "open"
        interval = int(self.session_length.get())
        while True:
            if time.time() - self.start > interval and time.time() - self.start < interval * 2:
                self.goal = "close"
            if time.time() - self.start > interval * 2 and time.time() - self.start < interval * 3:
                self.goal = "claw"
            if time.time() - self.start > interval * 3:
                self.goal = "open"
                start = time.time()


class StatusBar(Frame):

    def __init__(self, master):
        Frame.__init__(self, master, background='gray88')
        self.text = StringVar()
        self.label = Label(self,
                           anchor=W,
                           background='gray88',
                           textvariable=self.text,
                           foreground='dark slate gray')
        self.label.pack(fill=X, side=BOTTOM)

    def set(self, status):
        self.text.set(status)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text='')
        self.label.update_idletasks()


def showImage(filepath, root):
    img = Image.open(filepath)
    im = ImageTk.PhotoImage(img.resize((300, 300)))
    panel = Label(root, width=NOTEBOOK_WIDTH, height=NOTEBOOK_HEIGHT, image=im)
    panel.pack(expand=True)


if __name__ == "__main__":
    root = Window("Hand Therapy")
    root.geometry("300x300")
    showImage("C:\\Users\\Ca\\Desktop\\hand.jpg", root)
    root.mainloop()
