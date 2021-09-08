import ffmpeg
import cv2
from tkinter import *
from PIL import ImageTk, Image

import tkinter.ttk as ttk
from tkinter import filedialog
import cv2
import numpy as np
import datetime
import os

class Player(self):
    def __init__(self):
        self.root = Tk()

    def update_value():
        scale.config(value=frame)

    # var=IntVar(value=50)
    def set_fram(self,event):
        self.frame = self.scale.get()
        if int(self.frame) != self.frame:
            self.frame = round(self.frame)
        self.l.config(text=self.to_time(self.frame))
        self.run_video(frame)


    def design_window(self,title, geo, ico):
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
        canvas = Canvas(self.root
                        , width=560
                        , heigh=400,
                        bg='black')
        canvas.place(x=400, y=10)

        frame1 = ttk.LabelFrame(self.root, text='Fram Pos')
        frame1.place(x=10, y=420)

        self.scale = ttk.Scale(self.root, from_=0,
                          to=100, length=550,
                          orient='horizontal', value=0, state='disabled')
        self.scale.place(x=408, y=430)

        self.img = PhotoImage(file='front.png')
        canvas.create_image(0, 0, image=self.img, anchor=NW)
        self.fps = 25

        Click = IntVar()
        Click.set(frame_list[0])
        op = ttk.OptionMenu(tab1, Click, *frame_list, command=change_fram_p)
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
        op1 = ttk.OptionMenu(tab1, vc_click, *vc_list, command=change_vc)
        op1.place(x=63, y=10)
        op2 = ttk.OptionMenu(tab1, ac_click, *ac_list, command=change_ac)
        op2.place(x=123, y=10)
        op3 = ttk.OptionMenu(tab1, crf_click, *crf_list, command=change_crf)
        op3.place(x=203, y=10)
        op3 = ttk.OptionMenu(tab1, audio_click, *audio_list, command=change_audio)
        op3.place(x=10, y=50)

        scale.config(command=set_fram)
        # video_name is the video being called
        self.frame = 0
        i = to_time(frame)
        l = Label(frame1, text=i, bg='white')
        l.pack()
        self.frame_p = 1;
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
        notebook = ttk.Notebook(root)

        tab1 = ttk.Frame(notebook, width=380, height=380)
        tab2 = ttk.Frame(notebook, width=380, height=380)

        notebook.add(tab1, text='Tab 1')
        notebook.add(tab2, text='Tab 2')
        notebook.place(x=10, y=10)
        self.dic = {}

        b = ttk.Button(tab2, text='start trim', command=start_trim, state='disabled')
        b1 = ttk.Button(tab2, text='end trim', command=end_trim, state='disabled')
        con = ttk.Button(tab2, text='convert', command=convert_, state='disabled')
        b.place(x=10, y=10)
        b1.place(x=100, y=10)
        con.place(x=190, y=10)
        main_menu = Menu(root)
        root.config(menu=main_menu)
        menu = [
            Menu(main_menu, tearoff=0),
            Menu(main_menu, tearoff=0),
            Menu(main_menu, tearoff=0)
        ]
        main_menu.add_cascade(label='file', menu=menu[0])
        main_menu.add_cascade(label='edit', menu=menu[1])
        main_menu.add_cascade(label='option', menu=menu[2])

        menu[0].add_command(label='file')
        menu[0].add_command(label='New', command=MenuCom.open_file)
        menu[0].add_command(label='Exit', command=root.destroy)

        # bind
        root.bind("<Left>", move_video_left)
        root.bind("<Right>", move_video_right)

        root.mainloop()

    class MenuCom(self):
        def open_file():
            root.file_name = filedialog.askopenfilename(initialdir="e:",
                                                        title='select a video file',
                                                        filetypes=(("MKV file", "*.mkv"),
                                                                   ("VLC file", "*.ts"),
                                                                   ("MP4 file", "*.mp4"),
                                                                   ("All file", "*.*")))
            b.config(state='NORMAL')
            self.inp = ffmpeg.input(root.file_name)
            self.a = inp['a']
            self.v = inp['v']
            self.video = cv2.VideoCapture(root.file_name)

            self.fps = video.get(cv2.CAP_PROP_FPS)
            no_error = True

            self.frame = 0
            length_frame = video.get(cv2.CAP_PROP_FRAME_COUNT)

            scale.config(to=self.length_frame, value=0)
            scale.config(state='NORMAL')
            run_video(0)

    def to_time(self,fram_):
        return str(datetime.timedelta(seconds=fram_ / self.fps))

    def run_video(self,fram_num):
       try:
            l.config(text=to_time(fram_num))
            video.set(cv2.CAP_PROP_POS_FRAMES, fram_num);  # Where frame_no is the frame you want
            ret, self.frame = video.read()  # Read the frame

            self.img = ImageTk.PhotoImage(
                Image.fromarray(
                    cv2.cvtColor(
                        cv2.resize(
                            self.frame,
                            (560, 400),
                            interpolation=cv2.INTER_NEAREST),
                        cv2.COLOR_BGR2RGB)))
            canvas.create_image(0, 0, image=self.img, anchor=NW)
        except:
            pass


    def change_ac(self,event):
        self.dic['c:a'] = str(ac_click.get())

    def change_vc(self,event):
        self.dic['c:v'] = str(vc_click.get())

    def change_crf(self,event):
        self.dic['crf'] = str(crf_click.get())

    def change_fram_p(self,event):
        self.frame_p = Click.get()

    def change_audio(self,event):
        self.a = inp[str('a:' + str(audio_click.get()))]
        print(str('a:' + str(audio_click.get())))

    def move_video_right(self,event):
        if self.frame < self.length_frame:
            self.frame += self.frame_p

            self.scale.config(value=frame)
            self.run_video(self.frame)

    def move_video_left(self,event):
        if self.frame > 1:
            self.frame -= self.frame_p
            self.scale.config(value=self.frame)
            run_video(self.frame)

    def video(self):
        pass

    def start_trim(self):
        self.dic['ss'] = to_time(scale.get())
        b1.config(state='NORMAL')

    def end_trim(self):
        self.dic['to'] = to_time(self.scale.get())
        con.config(state='NORMAL')

    def convert_(self):
        global outfile
        out = filedialog.asksaveasfilename(defaultextension=".ts",
                                           initialdir="c:",
                                           title='save file')
        b1.config(state='disabled')
        b.config(state='NORMAL')
        con.config(state='disabled')
        self.outfile = ffmpeg.output(a, v, out, **self.dic)
        print(outfile.compile())
        if os.path.isfile(out):
            ffmpeg.run(outfile, overwrite_output=True, capture_stdout=True)
        else:
            ffmpeg.run(outfile)
