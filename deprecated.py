import random

import cv2
import numpy as np

from utils import managed_cv2_open_file, read_frame_from_vid, GAUSSIAN_SIZE, find_dark_lines, axes


def frame_sample_reader(video_file, blur_radius=None, frame_step=100):
    with managed_cv2_open_file(video_file) as video:
        length_frame = video.get(cv2.CAP_PROP_FRAME_COUNT)
        for frame_no in range(int(length_frame / 10), int(length_frame), frame_step):
            ret, frame = read_frame_from_vid(video, frame_no)
            if not ret:
                break
            if blur_radius:
                frame = cv2.GaussianBlur(frame, (blur_radius, blur_radius), 0)
            yield frame


def frame_stream_sample_reader(video_file, blur_radius=None, sample_size=200):
    reservoir = sample_size * [None]

    with managed_cv2_open_file(video_file) as video:
        frame_no, ret = -1, True
        while ret:
            frame_no = frame_no + 1
            if frame_no < sample_size:
                ret, frame = read_frame_from_vid(video, frame_no)
                reservoir[frame_no] = frame if ret else None
            else:
                do_replace = random.random() < (sample_size / frame_no)  # replace with probability n/t
                if do_replace:
                    replace_position = random.randint(0, sample_size - 1)
                    ret, frame = read_frame_from_vid(video, frame_no)
                    if ret:
                        reservoir[replace_position] = frame
        # length_frame = video.get(cv2.CAP_PROP_FRAME_COUNT)
        # print(f"Final frame: {frame_no}  , Officially: {length_frame}")
        # print(reservoir)
        for frame in reservoir:
            if frame is not None:
                if blur_radius:
                    # frame = cv2.GaussianBlur(frame, (blur_radius, blur_radius), 0)
                    frame = cv2.medianBlur(frame, 5)
                yield frame


def create_mean_std_frames_naive(all_frames):
    all_frames_expanded = [np.expand_dims(frame, axis=3) for _, frame in all_frames]
    all_frames_4d = np.concatenate(all_frames_expanded, axis=3)
    mean_frame = np.mean(all_frames_4d, axis=3)
    std_frame = np.std(all_frames_4d, axis=3)
    return mean_frame.astype(np.int8), std_frame / 255.0


def calc_std_per_pixel(video_file_name):
    sum_frames = None
    sum_variance = None

    # That assumes all frames are exactly the same size
    # for frame_no, frame in enumerate(frame_sample_reader(video_file_name, GAUSSIAN_SIZE)):
    for frame_no, frame in enumerate(frame_stream_sample_reader(video_file_name, GAUSSIAN_SIZE)):
        sum_frames = frame + (np.zeros_like(frame).astype('int64') if sum_frames is None else sum_frames)

    avg_frame = (sum_frames / frame_no).astype('int64')

    for frame_no, frame in enumerate(frame_sample_reader(video_file_name, GAUSSIAN_SIZE)):
        diff_from_avg = (frame.astype('int64') - avg_frame.astype('int64'))
        diff_from_avg = np.absolute(diff_from_avg).astype('int64')  # diff_from_avg ** 2 #
        sum_variance = diff_from_avg + (np.zeros_like(frame).astype('int64') if sum_variance is None else sum_variance)
    avg_variance = (sum_variance / frame_no)  # Created as float64

    return avg_frame, avg_variance


def find_dark_edges_globally(video_file_name):
    first_row_lst = []
    last_row_lst = []
    first_col_lst = []
    last_col_lst = []
    for frame_no, frame in enumerate(frame_sample_reader(video_file_name, GAUSSIAN_SIZE, 47)):
        img_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        first_row, last_row = find_dark_lines(img_gray, axes['ROWS'])
        first_col, last_col = find_dark_lines(img_gray, axes['COLUMNS'])

        first_row_lst.append(first_row)
        last_row_lst.append(last_row)
        first_col_lst.append(first_col)
        last_col_lst.append(last_col)

    # The first and last (line/column) which host the largest rectangle, in each of frame_no frames.
    img_statistics = list([first_row_lst, last_row_lst, first_col_lst, last_col_lst]);
    img_percentiles = np.percentile(img_statistics, [5, 20, 30, 50, 80, 95], axis=1)
    img_percentiles = np.around(img_percentiles).astype(int)

    # first_row_final, last_row_final, first_col_final, last_col_final =
    final_result = img_percentiles[4]  # first_row_final, last_row_final, first_col_final, last_col_final

    return final_result[2:4], final_result[0:2]
