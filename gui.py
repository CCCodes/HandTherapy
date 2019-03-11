from tkinter import *

from PIL import ImageTk


HEAD = ("Arial", 16)
FONT = ("Arial", 10)
COURIER = ("Courier New", 12)

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 440
NOTEBOOK_WIDTH = 430
NOTEBOOK_HEIGHT = 300

NOTEBOOK_COLOR = 'white'

GUI_DEBUG = False



class Window(Tk):

    def __init__(self, title, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.wm_resizable(0, 0)
        self.title(title)
        self.wm_iconbitmap("images\doublehelix.ico")
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

        self.container = frame(self)
        self.container.pack(side='top', fill='both', expand=True)

        # sub_container for options bar
        self.sub_container = Frame(self.container)
        self.sub_container.pack()

        self.side_bar = OptionsBar(self.sub_container, self)
        self.side_bar.grid(column=0, rowspan=3, pady=10)

        self.pb_space = Frame(self.container, {'height': 50,
                                               'width': 500,
                                               'background': 'red'})

        # pady 2nd param also controls status bar placement
        # if the window was resizable it would be placed incorrectly
        self.pb_space.pack(pady=10)

        self.bar = ProgressWin(self.pb_space, self)

        self.status_bar = StatusBar(self.container)
        self.status_bar.pack(side="bottom", fill=X, expand=True, anchor='s')
        self.status_bar.set("Ready")

        # =================
        # NOTEBOOK AND TABS
        # =================

        self.nbk = ttk.Notebook(self.sub_container, width=NOTEBOOK_WIDTH,
                                height=NOTEBOOK_HEIGHT)

        self.nbk.bind('<<NotebookTabChanged>>', self.change_tabs)

        # contains ttk.Frame type for adding and showing frames
        self.frames = {}
        self.custom_frames = {}  # contains custom types for accessing elements

        # AdvancedPage is before FormPage because FormPage init needs to access
        # its methods (save and import_entries)
        for F in (StartPage, AdvancedPage, FormPage, OutputPage):
            frame = ttk.Frame(self.nbk)
            custom = F(frame, self, {'background': NOTEBOOK_COLOR,
                                     'highlightthickness': '4',
                                     'highlightcolor': 'gray90'})
            custom.pack(expand=True, fill=BOTH, side=TOP)
            custom.tkraise()

            # instead of the class as the key, the string is the key
            self.frames[str(F)[15:-2]] = frame
            self.custom_frames[str(F)[15:-2]] = custom

        self.nbk.grid(row=1, column=1, sticky='nsew', padx=(0, 20), pady=(20,
                                                                          5))

        # ========
        # MENU BAR
        # ========

        self.menubar = Menu(self)

        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="New Process",
                             command=lambda: self.show_frame('FormPage'))
        filemenu.add_command(label="Convert", command=self.convert)

        filemenu.add_separator()

        settingsmenu = Menu(filemenu, tearoff=0)
        settingsmenu.add_command(label="Change Color",
                                 command=self.change_color)

        advanced_page_ = self.custom_frames['AdvancedPage']
        settingsmenu.add_command(label="Import Settings")
        settingsmenu.add_command(label="Save Settings")
        filemenu.add_cascade(label="Settings", menu=settingsmenu)

        entriesmenu = Menu(filemenu, tearoff=0)
        entriesmenu.add_command(label="Import Entries")
        entriesmenu.add_command(label="Save Entries",
                                command=advanced_page_.save)
        filemenu.add_cascade(label="Entries", menu=entriesmenu)

        self.menubar.add_cascade(label="File", menu=filemenu)  # index = 0

        editmenu = Menu(self.menubar, tearoff=0)
        editmenu.add_command(label="Main Form",
                             command=lambda: self.show_frame('FormPage'))
        editmenu.add_command(label="Reset", command=self.reset)
        self.menubar.add_cascade(label="Edit", menu=editmenu)  # index = 1

        self.show_status = BooleanVar()
        self.show_status.set(True)
        viewmenu = Menu(self.menubar, tearoff=0)
        viewmenu.add_checkbutton(label="Status bar",
                                 command=self.status_bar_toggle,
                                 variable=self.show_status,
                                 onvalue=True,
                                 offvalue=False)
        self.menubar.add_cascade(label="View", menu=viewmenu)  # index = 2

        runmenu = Menu(self.menubar, tearoff=0)
        runmenu.add_command(label="Run Process")
        runmenu.add_command(label="Save and Stop", command=self.save_and_quit)
        runmenu.add_command(label="Stop", command=self.complete)
        runmenu.add_command(label="Exit", command=sys.exit)
        self.menubar.add_cascade(label="Run", menu=runmenu)

        graphmenu = Menu(self.menubar, tearoff=0)
        graphmenu.add_command(label="Word Cloud", command=self.display_cloud)
        self.menubar.add_cascade(label="Graph", menu=graphmenu)

        advancedmenu = Menu(self.menubar, tearoff=0)
        advancedmenu.add_command(label="Options", command=
        lambda: self.show_frame('AdvancedPage'))
        self.menubar.add_cascade(label="Advanced", menu=advancedmenu)

        self.config(menu=self.menubar)
        self.menubar.bind('<<MenuSelect>>', self.status_bar_update)

        # ==========
        # POPUP MENU
        # ==========

        self.popup = Menu(self, tearoff=0)
        self.popup.add_command(label='Close', command=self.close_tab)
        self.popup.add_command(label='Open All Tabs',
                               command=self.open_all_tabs)
        self.popup_index = None

        self.frame_indexes = {}
        self.current_frame = None
        self.add_frame('StartPage')

        self.update_color()

    def status_bar_toggle(self):
        if self.status_bar.label.winfo_ismapped():
            self.status_bar.pack_forget()
        else:
            self.status_bar.pack(side="bottom", fill="both", expand=True)

    def change_tags(self):
        pass

    def status_bar_update(self, event=None):
        index = self.call(event.widget, "index", "active")
        if index in range(0, len(self.messages)):
            self.status_bar.set(self.messages[index])
        else:
            self.status_bar.set("Ready")

    def show_frame(self, cont):
        """ Adds and displays new tabs of the notebook.

        :param cont: String title of the new frame being displayed
        :return: void
        """
        if cont == 'AdvancedPage' and \
                str(self.frames['FormPage']) not in self.nbk.tabs():
            self.show_frame('FormPage')
        if str(self.frames[cont]) not in self.nbk.tabs():
            self.add_frame(cont)
        self.nbk.select(self.frame_indexes[cont])
        self.current_frame = cont

    def add_frame(self, cont):
        frame = self.frames[cont]  # shows the frame that is called by class
        self.nbk.add(frame, text=cont[:-4])
        self.frame_indexes[cont] = self.nbk.index('end') - 1
        self.nbk.bind('<Button-3>', self.on_button_3)

    def on_button_3(self, event):
        if event.widget.identify(event.x, event.y) == 'label':
            self.popup_index = event.widget.index('@%d,%d' % (event.x, event.y))
            try:
                self.popup.tk_popup(event.x_root + 57, event.y_root + 11, 0)
            finally:
                self.popup.grab_release()

    def close_tab(self):

        # if there is more than one tab open
        if self.nbk.index('end') > 1 and self.popup_index is not None:
            self.nbk.hide(self.popup_index)
            self.popup_index = None

    def open_all_tabs(self):
        tabs = ['StartPage', 'FormPage', 'AdvancedPage']
        for tab in tabs:
            self.show_frame(tab)

    def update_color(self):
        if not GUI_DEBUG:
            self.side_bar['bg'] = self.bg_color
            self.container['bg'] = self.bg_color
            self.sub_container['bg'] = self.bg_color
            self.pb_space['bg'] = self.bg_color

    def reset(self):
        self.bg_color = 'powder blue'
        self.update_color()

        self.custom_frames['FormPage'].set_filename("Select file...")
        main.form_elements['filename'] = None
        self.custom_frames['FormPage'].ents["Email"].delete(0, END)
        self.custom_frames['FormPage'].ents["Keywords"].delete(0, END)
        self.custom_frames['FormPage'].v2.set("Select file...")
        main.form_elements['filename'] = None

        advanced_page_ = self.custom_frames['AdvancedPage']
        advanced_page_.auto_manual_columns.set('AUTO')
        advanced_page_.symbol_col.delete(0, END)
        advanced_page_.symbol_col.config(state='disabled')
        advanced_page_.synonyms_col.delete(0, END)
        advanced_page_.synonyms_col.config(state='disabled')
        advanced_page_.v.set("ALL")
        advanced_page_.entry.delete(0, END)
        advanced_page_.entry.config(state="disabled")
        advanced_page_.desc.set(0)
        advanced_page_.sort.set(0)

    def convert(self):
        root = ConvertPrompt(self)
        root.mainloop()

    def display_cloud(self):
        output_file = makecloud.generate_word_cloud()
        self.show_frame('OutputPage')
        self.custom_frames['OutputPage'].display_image(output_file)

    @staticmethod
    def complete():
        main.ask_quit = True

    @staticmethod
    def save_and_quit():
        main.ask_save_and_quit = True


class ConvertPrompt(Toplevel):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.title("Convert File")
        self.master = master

        self.file_opt = options = {}
        options['defaultextension'] = '.txt'
        options['filetypes'] = [('text files', '.txt')]
        options['initialdir'] = "C:\\Users\\%s\\" % getpass.getuser()
        options['parent'] = master
        options['title'] = "Choose a file"

        self.grid_columnconfigure(1, weight=1)
        msg = Label(self, text="Convert tab delineated .txt to .xlsx.")
        msg.grid(row=0, columnspan=3, pady=(10, 4), padx=5)
        lab = Label(self, text="Text file: ")
        lab.grid(row=1, column=0, padx=5)

        # this stores the displayed version of the filename
        self.v_display = StringVar()
        b1 = ttk.Button(self, text="Browse...", command=self.askopenfilename)
        b1.grid(row=1, column=1, padx=5)
        self.geometry('190x80+300+300')

    def askopenfilename(self):
        file = tkinter.filedialog.askopenfilename(**self.file_opt)
        if not file:
            return
        with open(file, 'r') as f:
            unsplit_rows = f.read().split('\n')
        split_rows = []
        for row in unsplit_rows:
            split_rows.append(row.split('\t'))
        converted_wb = openpyxl.Workbook()
        ws_input = converted_wb.active
        ws_input.title = 'Input'
        main.write_rows(split_rows, ws_input)
        save_name = file[:-4] + '.xlsx'
        # TODO program gives error "select a file to sort" even though the
        # words are displayed
        try:
            converted_wb.save(save_name)

        # if the user tries to save it in C: or somewhere inaccessible
        except PermissionError:
            # it will be saved in the current directory
            converted_wb.save(save_name.split('/')[-1])
        self.master.show_frame('FormPage')
        self.master.custom_frames['FormPage'].set_filename(save_name)

        self.destroy()


class StatusBar(Frame):

    def __init__(self, master):
        super().__init__(master)
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


class OptionsBar(Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent)
        Frame.__init__(self, parent, *args, **kwargs)
        self.controller = controller

        info_image = ".\images\Information.png"
        self.b1, self.photo = self.button_from_label("Info",
                                                     info_image,
                                                     self.info_button,
                                                     "Get information and help"
                                                     " about new features")
        self.b1.grid(row=0, padx=(20, 0), pady=15)

        self.b2, self.photo2 = self.button_from_label("New",
                                                      ".\images\Search.png",
                                                      self.new_button,
                                                      "Process another input "
                                                      "file to get citations.")
        self.b2.grid(row=1, padx=(20, 0), pady=15)

    def button_from_label(self, text, image_url, cmd, status):
        image = Image.open(image_url)
        image = image.resize((30, 30))
        photo = ImageTk.PhotoImage(image)
        btn = Label(self,
                    text=text,
                    image=photo,
                    compound=TOP,
                    width=70,
                    bg="blue",
                    cursor='hand2')
        btn.bind('<Button-1>', cmd)
        btn.bind('<Enter>', lambda e: (btn.config(bg='light cyan'),
                                       self.controller.status_bar.set(status)))
        btn.bind('<Leave>', lambda e:
        (btn.config(bg=NOTEBOOK_COLOR),
         self.controller.status_bar.set('Ready')))
        btn.bind('<ButtonRelease-1>', lambda e: btn.config(bg='light cyan'))
        return btn, photo

    def info_button(self, _):
        self.b1.config(bg='LightSlateGray')
        self.controller.show_frame('StartPage')

    def new_button(self, _):
        self.b2.config(bg='LightSlateGray')
        self.controller.show_frame('FormPage')


class StartPage(Frame):

    def __init__(self, parent, controller, *args, **kwargs):
        super(StartPage, self).__init__(parent, *args, **kwargs)
        # Frame.__init__(parent, *args, **kwargs)
        padding_x = round(NOTEBOOK_WIDTH / 7)
        padding_y = round(NOTEBOOK_HEIGHT / 9)
        self.controller = controller
        self.previous_color = controller.bg_color

        lab = Label(self, text="Welcome to BioDataSorter", font=HEAD,
                    background=NOTEBOOK_COLOR, cursor='heart')
        lab.grid(row=0, pady=padding_y)
        # lab.bind('<Button-1>', self.surprise_color)
        lab.bind('<Leave>', lambda e:
        # current color is reset
        (controller.change_color(self.previous_color),
         controller.status_bar.set('Ready')))

        get_started = Label(self,
                            text="Click New to get started or File>Convert \n "
                                 "a text file from GEO profile data.",
                            background='white',
                            font=FONT)
        get_started.grid(row=1)

        separator = Frame(self, height=1, width=NOTEBOOK_WIDTH, bg='dark gray')
        separator.grid(row=2)

        underline = font.Font(font="arial 10 underline italic")
        self.github_link = "https://github.com/BioDataSorter/BioDataSorter"

        self.copy_link_popup = Menu(controller, tearoff=0)
        cb_append = controller.clipboard_append
        self.copy_link_popup.add_command(label='Copy Link',
                                         command=lambda:
                                         cb_append(self.github_link))
        self.copy_link_popup.add_command(label='Open Link in Browser',
                                         command=self.launch_page)

        lab2 = Label(self,
                     text="Visit our GitHub repository for more information",
                     background=NOTEBOOK_COLOR,
                     cursor='hand2',
                     font=underline)
        lab2.grid(row=3, pady=10)
        lab2.bind('<Enter>', lambda e: (lab2.config(foreground='blue'),
                                        controller.status_bar.set(
                                            self.github_link)))
        lab2.bind('<Leave>', lambda e: (lab2.config(foreground='black'),
                                        controller.status_bar.set('Ready')))
        lab2.bind('<Button-1>', self.launch_page)
        lab2.bind('<Button-3>', self.on_button_3)

        # weight of rows (title should take up more space and rest on bottom)
        # should fix problem of getting cut off
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)

    def launch_page(self, _=None):
        webbrowser.open_new_tab(self.github_link)

    def surprise_color(self, _):
        self.previous_color = self.controller.bg_color
        self.controller.change_color('red')
        self.controller.status_bar.set('Awww... we love you too!')

    def on_button_3(self, event):
        try:
            self.copy_link_popup.tk_popup(event.x_root + 75,
                                          event.y_root + 11,
                                          0)
        finally:
            self.copy_link_popup.grab_release()