import random

import cv2
import numpy
import numpy as np
from contextlib import contextmanager

axes = {'COLUMNS': 0, 'ROWS': 1}
GAUSSIAN_SIZE = 15


def read_frame_from_vid(video, frame_no):
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_no)  # 0-based index of the frame to be decoded/captured next.
    ret, frame = video.read()  # Read the frame
    # frame = frame[70:140, 1400:, :]
    return ret, frame


@contextmanager
def managed_cv2_open_file(*args, **kwds):
    # Code to acquire resource
    video_file_handler = cv2.VideoCapture(*args, **kwds)
    try:
        yield video_file_handler
    finally:
        # Code to release resource
        video_file_handler.release()


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
                    frame = cv2.GaussianBlur(frame, (blur_radius, blur_radius), 0)
                yield frame


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


def show(img, normalize=False, window=False):
    img_display = 255 * img / img.max() if normalize else img
    img_display = img_display[70:140, 1400:, :] if window else img_display
    cv2.imshow('image', (img_display.astype('uint8')))
    cv2.waitKey(0)


def pct(x):
    return np.percentile(x.flatten(), [5, 10, 50, 90, 99, 100], axis=0)


def mask_frame_by_variance(avg_variance, opencv_frame_left):
    avg_variance_monochrome = np.sum(avg_variance, axis=2) / 3  # Add variances for RGB components
    _, mask = cv2.threshold(avg_variance_monochrome, thresh=10, maxval=200, type=cv2.THRESH_BINARY)
    masked = cv2.bitwise_and(opencv_frame_left, opencv_frame_left, mask=mask.astype('uint8'))
    return masked


def find_longest_gap(seq):
    # Input is a sorted array of numbers (representing rows or columns).
    # Returns the beginning and end positions of the longest gap in the series
    longest_position = -1
    longest_gap = -1
    for pos, val in enumerate(seq[:-1]):
        gap = seq[pos + 1] - seq[pos]
        if gap > 1 and gap > longest_gap:
            longest_position = pos
            longest_gap = gap
    if longest_position > -1:
        return seq[longest_position] + 1, seq[longest_position + 1] - 1
    else:
        return 0, max(seq)


def find_dark_lines(greyscale_image, axis):
    percentiles = np.percentile(greyscale_image, [5, 50, 99, 100], axis=axis)
    # res = (percentiles[0] < 10) & ((percentiles[1] < 10) | (percentiles[1] < 20) | (percentiles[2] < 20) | (percentiles[2] > 150))
    res = (percentiles[3] < 20) | (
            (percentiles[2] < 20) & (percentiles[3] > 150))  # Most of the pixels in line are very dark or very bright
    # Value is true in positions where possibly

    lines_numbers = sorted([x[0] for x in np.argwhere(res)])
    if len(lines_numbers) == 0:
        return 0, len(res) - 1
    else:
        return find_longest_gap(lines_numbers)

# if __name__ == '__main__':
#     arr = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
#            30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
#            57, 58, 59, 60, 61, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93,
#            94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 626, 627, 628, 629, 630, 631, 632, 633,
#            634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655,
#            656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677,
#            678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699,
#            700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719]
#
#     beginning, end = find_longest_gap(arr)
#     print(f'beginning={beginning}, end={end}')
