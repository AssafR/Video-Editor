import cv2
import datetime
import os
import ffmpeg
import tkinter.ttk as ttk
import utils
from utils import mask_frame_by_variance, find_dark_lines

from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
import numpy as np

DEFAULT_HEIGHT = 400

DEFAULT_WIDTH = 560

THRESHOLD = 5


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
        self.first_row_final = None
        self.last_row_final = None
        self.first_col_final = None
        self.last_col_final = None
        self.frame = None
        self.frame_no = None
        self.scale = None
        self.fps = None
        self.img_left = None
        self.img_right = None
        self.avg_frame = None
        self.avg_variance = None
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
        self.left_image_on_canvas = None
        self.right_image_on_canvas = None
        self.btn_start_trim = None
        self.btn_end_trim = None
        self.btn_convert = None
        self.time_label = None
        self.crop_label = None
        self.resolution_label = None

    def update_value(self):
        self.scale.config(value=self.frame_no)

    # var=IntVar(value=50)
    def set_frame_no(self, event):
        self.frame_no = self.scale.get()
        if int(self.frame_no) != self.frame_no:
            self.frame_no = round(self.frame_no)
        self.time_label.config(text=self.to_time(self.frame_no))
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
                                  width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT,
                                  bg='black')
        self.left_canvas.place(x=200, y=10)

        self.right_canvas = Canvas(self.root,
                                   width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT,
                                   bg='black')
        self.right_canvas.place(x=760, y=10)

        frame1 = ttk.LabelFrame(self.root, text='Frame Pos')
        frame1.place(x=50, y=420)
        frame2 = ttk.LabelFrame(self.root, text='Cropping')
        frame2.place(x=150, y=420)
        frame3 = ttk.LabelFrame(self.root, text='Resolution')
        frame3.place(x=300, y=420)

        # Defining a Scale (i.e. Slider widget in this case).
        self.scale = ttk.Scale(self.root, from_=0,
                               to=100, length=550,
                               orient='horizontal', value=0, state='disabled')
        self.scale.place(x=408, y=430)

        self.img_left = PhotoImage(file='left.png')
        self.left_image_on_canvas = self.left_canvas.create_image(0, 0, image=self.img_left, anchor=NW)
        self.img_right = PhotoImage(file='right.png')
        self.right_image_on_canvas = self.right_canvas.create_image(0, 0, image=self.img_right, anchor=NW)
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
        self.time_label = Label(frame1, text=frame_no_as_time_str, bg='yellow')
        self.time_label.pack()
        self.crop_label = Label(frame2, text='', bg='yellow')
        self.crop_label.pack()
        self.resolution_label = Label(frame3, text='', bg='yellow')
        self.resolution_label.pack()

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

        menu[0].add_command(label='Open', command=self.open_file)
        # menu[0].add_command(label='file')
        menu[0].add_command(label='Exit', command=self.root.destroy)

        # bind
        self.root.bind("<Left>", self.move_video_left)
        self.root.bind("<Right>", self.move_video_right)

        self.root.mainloop()

    def to_time(self, frame_number):
        return str(datetime.timedelta(seconds=frame_number / self.fps))

    def prepare_to_present_image(self, opencv_frame, width, height):
        return ImageTk.PhotoImage(
            Image.fromarray(
                cv2.resize(
                    opencv_frame,
                    (width, height),
                    interpolation=cv2.INTER_CUBIC)
            )
        )

    def update_canvas_with_frame(self, canvas, image_on_canvas, frame):
        width, height = int(canvas['width']), int(canvas['height'])
        img = self.prepare_to_present_image(frame, width, height)
        canvas.itemconfig(image_on_canvas, image=img)
        return img

    def draw_rectangle_over_image(self, img, start_point, end_point):

        # start_point = (5, 5)
        # # Ending coordinate, here (220, 220)
        # # represents the bottom right corner of rectangle
        # end_point = (220, 220)
        if start_point[0] is None \
                or start_point[1] is None \
                or end_point[0] is None \
                or end_point[1] is None:
            return img

        color = (0, 255, 0)  # Green color in GRB

        # Line thickness of 2 px
        thickness = 3

        # Using cv2.rectangle() method
        # Draw a rectangle with blue line borders of thickness of 2 px
        image = cv2.rectangle(img, start_point, end_point, color, thickness)

        # # Displaying the image
        # cv2.imshow(window_name, image)
        return image

    def find_dark_edges(self, img_gray, axis):

        # Note, if axis=1 then semantically left->top, right->bottom

        average_axis = np.average(img_gray, axis=axis)  # Average each column, shape: (1280,)
        left_margin = np.argmin(average_axis <= THRESHOLD)
        average_axis_reverse = average_axis[::-1]  # Reverse column order
        left_margin_reverse = np.argmax(average_axis_reverse > THRESHOLD)
        # Last small value to the left: average_axis[left_margin-1]
        right_margin = len(average_axis_reverse) - left_margin_reverse - 1
        # First small value to the right : average_axis[right_margin + 1]

        left_margin = left_margin if left_margin > 0 else None
        right_margin = right_margin if right_margin < len(average_axis) - 1 else None

        return left_margin, right_margin

    def find_dark_edges_or_subtitles(self, img_search, img_draw):

        # img_gray = cv2.cvtColor(img_search, cv2.COLOR_RGB2GRAY)
        height, width, _ = img_search.shape  # e.g: (1080, 1920)
        #
        # first_row, last_row = find_dark_lines(img_gray, utils.axes['ROWS'])
        # first_col, last_col = find_dark_lines(img_gray, utils.axes['COLUMNS'])

        img_return = img_draw
        if self.first_row_final > -1 and self.last_row_final > -1:
            img_return = cv2.rectangle(img_return,
                                       (0, 0), (width - 1, self.first_row_final - 1), (0, 255, 0), thickness=-1)
            img_return = cv2.rectangle(img_return,
                                       (0, self.last_row_final + 1), (width - 1, height - 1), (0, 255, 0), thickness=-1)
        else:
            self.first_row_final = 0
            self.last_row_final = height - 1

        if self.first_col_final > -1 and self.last_col_final > -1:
            img_return = cv2.rectangle(img_return,
                                       (0, 0), (self.first_col_final - 1, height - 1), (0, 255, 0), thickness=-1)
            img_return = cv2.rectangle(img_return,
                                       (self.last_col_final + 1, 0), (width - 1, height - 1), (0, 255, 0), thickness=-1)
        else:
            self.first_col_final = 0
            self.last_col_final = width - 1

        img_return = img_return[
                     self.first_row_final:self.last_row_final,
                     self.first_col_final:self.last_col_final,
                     :]

        # for row_number in rows_numbers:
        #     img_return = cv2.line(img_return, (0, row_number), (width - 1, row_number), (0, 255, 0), thickness=1)

        # columns_numbers = self.find_dark_lines(img_gray, utils.axes['COLUMNS'])
        # for column_number in columns_numbers:
        #     img_return = cv2.line(img_return, (column_number,0), (column_number, height-1), (0, 255, 0), thickness=1)
        # points = np.array(points, np.int32).reshape((-1, 1, 2))
        #
        # color = (0, 255, 0)
        # thickness = 1
        #
        # img = cv2.polylines(img, [points], False, color, thickness)

        return img_return  # img_search #

    def calculate_crop_img(self, img):

        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        left_margin, right_margin = self.find_dark_edges(img_gray, utils.axes['COLUMNS'])
        top_margin, bottom_margin = self.find_dark_edges(img_gray, utils.axes['ROWS'])
        return left_margin, right_margin, top_margin, bottom_margin

    def process_image_old(self, img):
        height, width, _ = img.shape  # e.g: (1080, 1920, 3)
        left_margin, right_margin, top_margin, bottom_margin = self.calculate_crop_img(img)
        print(left_margin, right_margin, top_margin, bottom_margin)

        new_img = img
        new_img = self.draw_rectangle_over_image(new_img, (4, 4), (left_margin, height))
        new_img = self.draw_rectangle_over_image(new_img, (right_margin, 0), (width, height))
        new_img = self.draw_rectangle_over_image(new_img, (0, 0), (width, top_margin))
        new_img = self.draw_rectangle_over_image(new_img, (0, bottom_margin), (width, height))
        return new_img

    def process_image_flip(self, img):
        return cv2.flip(img, 1)

    def process_image(self, img):
        img_new = self.find_dark_edges_or_subtitles(img)
        return img_new

    def run_video(self, frame_number):
        # Called when a file is loaded and whenever an event causes change of frame (e.g. pressing left arrow).
        # self.img_right = self.update_canvas_with_frame(self.right_canvas, self.right_image_on_canvas,
        #                                                avg_frame)

        try:
            self.time_label.config(text=self.to_time(frame_number))  # Update the label
            ret, self.frame = utils.read_frame_from_vid(self.video, frame_number)
            if not ret:
                return False
            opencv_frame_left = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            # to prevent the image garbage collected.
            self.img_left = self.update_canvas_with_frame(self.left_canvas, self.left_image_on_canvas,
                                                          opencv_frame_left)
            # width, height = int(self.left_canvas['width']), int(self.left_canvas['height'])
            # img = self.prepare_to_present_image(self.frame, width, height)
            # img = self.img_right if (frame_number % 2 == 1) else img
            # self.img_left = img
            # # self.left_canvas.create_image(0, 0, image=img, anchor=NW)
            # self.left_canvas.itemconfig(self.left_image_on_canvas, image=self.img_left)
            #

            # self.img_left = self.prepare_to_present_image(opencv_frame_left)
            # self.left_canvas.create_image(0, 0, image=self.img_left, anchor=NW)

            # avg_frame = self.avg_frame.astype('uint8')
            # opencv_frame_right = self.process_image_flip(self.process_image_flip(avg_frame)).astype('uint8')
            # np.sum(self.avg_variance,axis=2).shape
            # avg_variance_monochrome = (255 * avg_variance_monochrome / avg_variance_monochrome.max()).astype('uint8')

            # The mask identified areas of very little change across the video and blacks them.
            avg_variance = self.avg_variance
            masked = opencv_frame_left  # mask_frame_by_variance(avg_variance, opencv_frame_left)
            img_drawn = self.find_dark_edges_or_subtitles(masked, opencv_frame_left)

            self.img_right = self.update_canvas_with_frame(
                self.right_canvas, self.right_image_on_canvas, img_drawn)

            # self.update_canvas_with_frame(self.right_canvas, self.right_image_on_canvas, opencv_frame_right)
            # self.img_right = self.prepare_to_present_image(opencv_frame_right)
            # self.right_canvas.create_image(0, 0, image=self.img_right, anchor=NW)
            return True

        except Exception as exception:
            print(exception)
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
            frame_no = self.frame_no + self.frame_p
            self.scale.config(value=frame_no)
            if self.run_video(frame_no):
                self.frame_no = frame_no

    def move_video_left(self, event):
        if self.frame_no > 1:
            frame_no = self.frame_no - self.frame_p
            self.scale.config(value=frame_no)
            if self.run_video(frame_no):  # Managed to read and display the frame
                self.frame_no = frame_no

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
        self.avg_frame, self.avg_variance = utils.calc_std_per_pixel(self.root.file_name)

        self.cropping_values_x, self.cropping_values_y = utils.find_dark_edges_globally(self.root.file_name)
        self.crop_label.config(
            text=f'{self.cropping_values_x[0]}:{self.cropping_values_x[1]} , {self.cropping_values_y[0]}:{self.cropping_values_y[1]}')
        resolution_x = self.cropping_values_x[1] - self.cropping_values_x[0] + 1
        resolution_y = self.cropping_values_y[1] - self.cropping_values_y[0] + 1
        res_str = f'{resolution_x}x{resolution_y}'
        self.resolution_label.config(text=res_str)

        self.first_col_final, self.last_col_final = self.cropping_values_x
        self.first_row_final, self.last_row_final = self.cropping_values_y

        self.frame_no = 1500  # Temporary
        self.run_video(self.frame_no)
