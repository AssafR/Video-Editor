import ffmpeg
from tkinter import *
from PIL import ImageTk, Image
import tkinter.ttk as ttk
from tkinter import filedialog
import cv2
import datetime
import os
import numpy as np


class Player:
    frame_list = [
        0,
        1,
        10,
        20,
        30,
        40,
        100,
        200
    ]

    def __init__(self):
        self.root = Tk()
        self.frame = None
        self.frame_no = None
        self.l = None
        self.scale = None
        self.fps = None
        self.img = None
        self.frame_p = None
        self.dic = {}
        self.b = None
        self.b1 = None
        self.con = None
        self.length_frame = 0
        self.no_error = None
        self.video = None
        self.canvas = None

    def update_value(self):
        self.scale.config(value=self.frame_no)

    # var=IntVar(value=50)
    def set_frame_no(self, event):
        self.frame_no = self.scale.get()
        if int(self.frame_no) != self.frame_no:
            self.frame_no = round(self.frame_no)
        self.l.config(text=self.to_time(self.frame_no))
        self.run_video(self.frame_no)

    def design_window(self, title, geo, ico):
        self.root.title(title)
        self.root.geometry(geo)
        self.root.iconbitmap(ico)
        self.root.configure(bg='white')

    def playermain(self):

        self.design_window('Video Editor', "1000x490", 'icon.ico')
        s = ttk.Style()

        s.configure('TFrame', background='white')
        s.configure('TNotebook', background='white')
        s.configure('TScale', background='white')
        s.configure('TLabelframe', background='white')
        self.canvas = Canvas(self.root
                        , width=560
                        , heigh=400,
                        bg='black')
        self.canvas.place(x=400, y=10)

        frame1 = ttk.LabelFrame(self.root, text='Fram Pos')
        frame1.place(x=10, y=420)

        self.scale = ttk.Scale(self.root, from_=0,
                               to=100, length=550,
                               orient='horizontal', value=0, state='disabled')
        self.scale.place(x=408, y=430)

        self.img = PhotoImage(file='front.png')
        self.canvas.create_image(0, 0, image=self.img, anchor=NW)
        self.fps = 25

        notebook = ttk.Notebook(self.root)

        tab1 = ttk.Frame(notebook, width=380, height=380)
        tab2 = ttk.Frame(notebook, width=380, height=380)

        Click = IntVar()
        Click.set(self.frame_list[0])
        op = ttk.OptionMenu(tab1, Click, self.frame_list, command=self.change_fram_p)
        op.place(x=10, y=10)
        vc_click = StringVar()
        ac_click = StringVar()
        crf_click = StringVar()
        audio_click = IntVar()
        vc_list = [
            'ac3',
            'ac3',
            'copy'
        ]
        ac_list = [
            'libx264',
            'libx264',
            'copy'
        ]

        crf_list = [
            'copy',
            'copy',
            '20',
            '25'
        ]
        audio_list = [
            0,
            0,
            1
        ]

        self.scale.config(command=self.set_frame_no)
        # video_name is the video being called
        self.frame_no = 0
        i = self.to_time(self.frame_no)
        self.l = Label(frame1, text=i, bg='white')
        self.l.pack()
        self.frame_p = 1
        op1 = ttk.OptionMenu(tab1, vc_click, *vc_list, command=self.change_vc)
        op1.place(x=63, y=10)
        op2 = ttk.OptionMenu(tab1, ac_click, *ac_list, command=self.change_ac)
        op2.place(x=123, y=10)
        op3 = ttk.OptionMenu(tab1, crf_click, *crf_list, command=self.change_crf)
        op3.place(x=203, y=10)
        op3 = ttk.OptionMenu(tab1, audio_click, *audio_list, command=self.change_audio)
        op3.place(x=10, y=50)

        notebook.add(tab1, text='Tab 1')
        notebook.add(tab2, text='Tab 2')
        notebook.place(x=10, y=10)

        self.b = ttk.Button(tab2, text='start trim', command=self.start_trim, state='disabled')
        self.b1 = ttk.Button(tab2, text='end trim', command=self.end_trim, state='disabled')
        self.con = ttk.Button(tab2, text='convert', command=self.convert_, state='disabled')
        self.b.place(x=10, y=10)
        self.b1.place(x=100, y=10)
        self.con.place(x=190, y=10)
        main_menu = Menu(self.root)
        self.root.config(menu=main_menu)
        menu = [
            Menu(main_menu, tearoff=0),
            Menu(main_menu, tearoff=0),
            Menu(main_menu, tearoff=0)
        ]
        main_menu.add_cascade(label='file', menu=menu[0])
        main_menu.add_cascade(label='edit', menu=menu[1])
        main_menu.add_cascade(label='option', menu=menu[2])

        menu[0].add_command(label='file')
        menu[0].add_command(label='New', command=self.open_file)
        menu[0].add_command(label='Exit', command=self.root.destroy)

        # bind
        self.root.bind("<Left>", self.move_video_left)
        self.root.bind("<Right>", self.move_video_right)

        self.root.mainloop()

    def to_time(self, fram_):
        return str(datetime.timedelta(seconds=fram_ / self.fps))

    def run_video(self, fram_num):
        try:
            self.l.config(text=self.to_time(fram_num))
            self.video.set(cv2.CAP_PROP_POS_FRAMES, fram_num);  # Where frame_no is the frame you want
            ret, self.frame = self.video.read()  # Read the frame

            self.img = ImageTk.PhotoImage(
                Image.fromarray(
                    cv2.cvtColor(
                        cv2.resize(
                            self.frame,
                            (560, 400),
                            interpolation=cv2.INTER_NEAREST),
                        cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.img, anchor=NW)
        except Exception as exception:
            pass

    def change_ac(self, event):
        self.dic['c:a'] = str(self.ac_click.get())

    def change_vc(self, event):
        self.dic['c:v'] = str(self.vc_click.get())

    def change_crf(self, event):
        self.dic['crf'] = str(self.crf_click.get())

    def change_fram_p(self, event):
        self.frame_p = self.Click.get()

    def change_audio(self, event):
        self.a = self.inp[str('a:' + str(self.audio_click.get()))]
        print(str('a:' + str(self.audio_click.get())))

    def move_video_right(self, event):
        if self.frame_no < self.length_frame:
            self.frame_no += self.frame_p
            self.scale.config(value=self.frame_no)
            self.run_video(self.frame_no)

    def move_video_left(self, event):
        if self.frame_no > 1:
            self.frame_no -= self.frame_p
            self.scale.config(value=self.frame_no)
            self.run_video(self.frame_no)

    def video(self):
        pass

    def start_trim(self):
        self.dic['ss'] = self.to_time(self.scale.get())
        self.b1.config(state='NORMAL')

    def end_trim(self):
        self.dic['to'] = self.to_time(self.scale.get())
        self.con.config(state='NORMAL')

    def convert_(self):
        out = filedialog.asksaveasfilename(defaultextension=".ts",
                                           initialdir="c:",
                                           title='save file')
        self.b1.config(state='disabled')
        self.b.config(state='NORMAL')
        self.con.config(state='disabled')
        self.outfile = ffmpeg.output(self.a, self.v, self.out, **self.dic)
        print(self.outfile.compile())
        if os.path.isfile(out):
            ffmpeg.run(self.outfile, overwrite_output=True, capture_stdout=True)
        else:
            ffmpeg.run(self.outfile)
    def open_file(self):
        self.root.file_name = filedialog.askopenfilename(initialdir="e:",
                                                         title='select a video file',
                                                         filetypes=(("MKV file", "*.mkv"),
                                                                    ("VLC file", "*.ts"),
                                                                    ("MP4 file", "*.mp4"),
                                                                    ("All file", "*.*")))
        self.b.config(state='NORMAL')
        self.inp = ffmpeg.input(self.root.file_name)
        self.a = self.inp['a']
        self.v = self.inp['v']
        self.video = cv2.VideoCapture(self.root.file_name)

        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.no_error = True

        self.frame_no = 0
        self.length_frame = self.video.get(cv2.CAP_PROP_FRAME_COUNT)

        self.scale.config(to=self.length_frame, value=0)
        self.scale.config(state='NORMAL')
        self.run_video(0)


# class MenuCom():
#     def __init__(self, root):
#         self.img = None
#         self.outfile = None
#         self.root = root
#         self.inp = None
#         self.a = None
#         self.fps = None
#
#
#     def open_file(self):
#         self.root.file_name = filedialog.askopenfilename(initialdir="e:",
#                                                          title='select a video file',
#                                                          filetypes=(("MKV file", "*.mkv"),
#                                                                     ("VLC file", "*.ts"),
#                                                                     ("MP4 file", "*.mp4"),
#                                                                     ("All file", "*.*")))
#         self.b.config(state='NORMAL')
#         self.inp = ffmpeg.input(self.root.file_name)
#         self.a = self.inp['a']
#         self.v = self.inp['v']
#         video = cv2.VideoCapture(self.root.file_name)
#
#         self.fps = video.get(cv2.CAP_PROP_FPS)
#         no_error = True
#
#         self.frame = 0
#         length_frame = video.get(cv2.CAP_PROP_FRAME_COUNT)
#
#         self.scale.config(to=self.length_frame, value=0)
#         self.scale.config(state='NORMAL')
#         self.run_video(0)
