import cv2
import datetime
import os
import ffmpeg
import tkinter.ttk as ttk

from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
from filters import flip_image


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

    ac_list = [
        'ac3',
        'ac3',
        'copy'
    ]
    vc_list = [
        'libx264',
        'libx264',
        'libx265',
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

    def __init__(self):
        self.frame = None
        self.frame_no = None
        self.scale = None
        self.fps = None
        self.img_left = None
        self.img_right = None
        self.frame_p = None
        self.params_dic = {}
        self.length_frame = 0
        self.video = None  # Will be filled with a cv2.VideoCapture object
        self.Click = None
        self.inp = None

        self.vc_click = None
        self.ac_click = None
        self.crf_click = None
        self.audio_click = None

        self.ffmpeg_a = None
        self.ffmpeg_v = None

        self.op1 = None
        self.op2 = None
        self.op3 = None

        self.root = Tk()
        self.left_canvas = None
        self.right_canvas = None
        self.btn_start_trim = None
        self.btn_end_trim = None
        self.btn_convert = None
        self.label = None

    def update_value(self):
        self.scale.config(value=self.frame_no)

    # var=IntVar(value=50)
    def set_frame_no(self, event):
        self.frame_no = self.scale.get()
        if int(self.frame_no) != self.frame_no:
            self.frame_no = round(self.frame_no)
        self.label.config(text=self.to_time(self.frame_no))
        self.run_video(self.frame_no)

    def design_window(self, title, geo, ico):
        self.root.title(title)
        self.root.geometry(geo)
        self.root.iconbitmap(ico)
        self.root.configure(bg='white')

    def player_main(self):

        self.design_window('Video Editor', "1500x490", 'icon.ico')
        s = ttk.Style()

        s.configure('TFrame', background='white')
        s.configure('TNotebook', background='white')
        s.configure('TScale', background='white')
        s.configure('TLabelframe', background='white')
        self.left_canvas = Canvas(self.root,
                                  width=560, height=400,
                                  bg='black')
        self.left_canvas.place(x=200, y=10)

        self.right_canvas = Canvas(self.root,
                                   width=560, height=400,
                                   bg='black')
        self.right_canvas.place(x=760, y=10)

        frame1 = ttk.LabelFrame(self.root, text='Frame Pos')
        frame1.place(x=100, y=420)

        # Defining a Scale (i.e. Slider widget in this case).
        self.scale = ttk.Scale(self.root, from_=0,
                               to=100, length=550,
                               orient='horizontal', value=0, state='disabled')
        self.scale.place(x=408, y=430)

        self.img_left = PhotoImage(file='left.png')
        self.left_canvas.create_image(0, 0, image=self.img_left, anchor=NW)
        self.img_right = PhotoImage(file='right.png')
        self.right_canvas.create_image(0, 0, image=self.img_right, anchor=NW)
        self.fps = 25

        notebook = ttk.Notebook(self.root)

        tab1 = ttk.Frame(notebook, width=180, height=380)
        tab2 = ttk.Frame(notebook, width=180, height=380)

        self.Click = IntVar()
        self.Click.set(self.frame_list[0])
        options_menu = ttk.OptionMenu(tab1, self.Click, self.frame_list, command=self.change_frame_p)
        options_menu.place(x=10, y=10)
        self.vc_click = StringVar()
        self.ac_click = StringVar()
        self.crf_click = StringVar()
        self.audio_click = IntVar()

        self.scale.config(command=self.set_frame_no)  # Set an event handler called upon changing the scale value
        # video_name is the video being called
        self.frame_no = 0
        frame_no_as_time_str = self.to_time(self.frame_no)
        self.label = Label(frame1, text=frame_no_as_time_str, bg='yellow')
        self.label.pack()

        self.frame_p = 1
        # Put all these menu selectors in place, 3 on top row and change_audio in bottom row.
        self.op1 = ttk.OptionMenu(tab1, self.vc_click, *self.vc_list, command=self.change_vc)
        self.op1.place(x=63, y=10)
        self.op2 = ttk.OptionMenu(tab1, self.ac_click, *self.ac_list, command=self.change_ac)
        self.op2.place(x=123, y=10)
        self.op3 = ttk.OptionMenu(tab1, self.crf_click, *self.crf_list, command=self.change_crf)
        self.op3.place(x=203, y=10)
        self.op3 = ttk.OptionMenu(tab1, self.audio_click, *self.audio_list, command=self.change_audio)
        self.op3.configure(state='disabled')
        self.op3.place(x=10, y=50)

        notebook.add(tab1, text='Tab 1')
        notebook.add(tab2, text='Tab 2')
        notebook.place(x=10, y=10)

        # Create all the widgets in tab2 and place them:
        self.btn_start_trim = ttk.Button(tab2, text='start trim', command=self.start_trim, state='disabled')
        self.btn_end_trim = ttk.Button(tab2, text='end trim', command=self.end_trim, state='disabled')
        self.btn_convert = ttk.Button(tab2, text='convert', command=self.convert_video, state='disabled')
        self.btn_start_trim.place(x=10, y=10)
        self.btn_end_trim.place(x=100, y=10)
        self.btn_convert.place(x=190, y=10)

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

        menu[0].add_command(label='New', command=self.open_file)
        menu[0].add_command(label='file')
        menu[0].add_command(label='Exit', command=self.root.destroy)

        # bind
        self.root.bind("<Left>", self.move_video_left)
        self.root.bind("<Right>", self.move_video_right)

        self.root.mainloop()

    def to_time(self, frame_number):
        return str(datetime.timedelta(seconds=frame_number / self.fps))

    def prepare_to_present_image(self, opencv_frame):
        return ImageTk.PhotoImage(
            Image.fromarray(
                cv2.resize(
                    opencv_frame,
                    (560, 400),
                    interpolation=cv2.INTER_CUBIC)
            ))

    def process_image(self, img):
        return flip_image(img)      

    def run_video(self, frame_number):
        # Called when a file is loaded and whenever an event causes change of frame (e.g. pressing left arrow).
        try:
            self.label.config(text=self.to_time(frame_number))  # Update the label
            self.video.set(cv2.CAP_PROP_POS_FRAMES,
                           frame_number);  # 0-based index of the frame to be decoded/captured next.

            ret, self.frame = self.video.read()  # Read the frame
            opencv_frame_left = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

            self.img_left = self.prepare_to_present_image(opencv_frame_left)
            self.left_canvas.create_image(0, 0, image=self.img_left, anchor=NW)

            opencv_frame_right = self.process_image(opencv_frame_left)
            self.img_right = self.prepare_to_present_image(opencv_frame_right)
            self.right_canvas.create_image(0, 0, image=self.img_right, anchor=NW)

        except Exception as exception:
            pass

    def change_ac(self, event):
        self.params_dic['c:a'] = str(self.ac_click.get())

    def change_vc(self, event):
        self.params_dic['c:v'] = str(self.vc_click.get())

    def change_crf(self, event):
        self.params_dic['crf'] = str(self.crf_click.get())

    def change_frame_p(self, event):
        self.frame_p = self.Click.get()

    def change_audio(self, event):
        if self.inp is not None:  # Temporary fix?
            self.ffmpeg_a = self.inp[str('a:' + str(self.audio_click.get()))]
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

    def start_trim(self):
        self.params_dic['ss'] = self.to_time(self.scale.get())
        self.btn_end_trim.config(state='NORMAL')

    def end_trim(self):
        self.params_dic['to'] = self.to_time(self.scale.get())
        self.btn_convert.config(state='NORMAL')

    def convert_video(self):
        out = filedialog.asksaveasfilename(defaultextension=".ts",
                                           initialdir="E:",
                                           title='save file')
        self.btn_end_trim.config(state='disabled')
        self.btn_start_trim.config(state='NORMAL')
        self.btn_convert.config(state='disabled')
        outfile = ffmpeg.output(self.ffmpeg_a, self.ffmpeg_v, out, **self.params_dic)
        # TODO: Doesn't support user cancel instead of save ...
        print(outfile.compile())
        if os.path.isfile(out):
            ffmpeg.run(outfile, overwrite_output=True, capture_stdout=True)
        else:
            ffmpeg.run(outfile)

    def open_file(self):
        self.root.file_name = filedialog.askopenfilename(initialdir="e:\\",
                                                         title='select a video file',
                                                         filetypes=(("MKV file", "*.mkv"),
                                                                    ("VLC file", "*.ts"),
                                                                    ("MP4 file", "*.mp4"),
                                                                    ("All file", "*.*")))
        self.op3.configure(state='enabled')  # Since we have a file, can choose a change_audio value
        self.btn_start_trim.config(state='NORMAL')
        self.inp = ffmpeg.input(self.root.file_name)
        self.ffmpeg_a = self.inp['a']
        self.ffmpeg_v = self.inp['v']
        self.video = cv2.VideoCapture(self.root.file_name)

        self.fps = self.video.get(cv2.CAP_PROP_FPS)

        self.frame_no = 0
        self.length_frame = self.video.get(cv2.CAP_PROP_FRAME_COUNT)

        self.scale.config(to=self.length_frame, value=0)
        self.scale.config(state='NORMAL')
        self.run_video(0)
