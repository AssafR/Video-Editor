import re
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from contextlib import contextmanager

from tqdm import tqdm

from deprecated import frame_sample_reader

axes = {'COLUMNS': 0, 'ROWS': 1}
GAUSSIAN_SIZE = 15


def opencv_display_image(img, window_name='image'):
    if img.shape[1] > 1280:
        img = cv2.resize(img, (int(img.shape[1] / 2), int(img.shape[0] / 2)))
    cv2.imshow(window_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def normalize_array(array):
    array_normalized = (array - np.min(array)) / (np.max(array) - np.min(array))
    return array_normalized


def read_frame_from_vid(video, frame_no):
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_no)  # 0-based index of the frame to be decoded/captured next.
    ret, frame = video.read()  # Read the frame
    # frame = frame[70:140, 1400:, :]
    return ret, frame


def get_number_frames(video_file):
    """
    Get the number of frames in a video file
    Note: This method might be inaccurate if the video file is corrupted or not in a standard format
    :param video_file: the video file (string)
    :return: the number of frames in the video file (int)
    """
    with managed_cv2_open_file(video_file) as video:
        return int(video.get(cv2.CAP_PROP_FRAME_COUNT))


def save_image(img, filename, img_format='jpg'):
    """
    Write image to file, similar to cv2.imwrite but compatible with non-utf names
    :param img: image
    :param filename: filename
    :param img_format: image format (e.g. "jpg")
    :return:
    """
    cv2.imencode(f".{img_format}", img)[1].tofile(filename)


def load_image(filename):
    """
    Load image from file, similar to cv2.imread but compatible with non-utf names
    :param filename: filename
    :return: image
    """
    return cv2.imdecode(np.fromfile(filename, np.uint8), cv2.IMREAD_COLOR)


def create_new_filename_with_suffix(video_file_name, target_dir, img_format, new_suffix):
    base_file_name = Path(video_file_name).stem
    new_stem_filename = f'{base_file_name}__{new_suffix}.{img_format}'
    new_path = Path(target_dir) / new_stem_filename
    return str(new_path)


def save_sample_of_frames_from_video_file(
        target_dir: str,
        video_file_name: str, min_no_samples: int, probability: float = None):
    """
    Save a sample of frames from a video file into a directory as images numbered by frame number
    :param probability:
    :param min_no_samples:
    :param target_dir:
    :param video_file_name:
    :return:
    """
    img_format = 'jpg'

    for frame_no, frame in (
            get_sample_of_frames_from_video_file(video_file_name, min_no_samples, probability)):
        new_suffix = f'{frame_no:06d}'
        new_path = create_new_filename_with_suffix(video_file_name, target_dir, img_format, new_suffix)
        save_image(frame, str(new_path))


def get_sample_of_frames_from_directory_or_video_file(
        image_cache_dir: str,
        video_file: str, min_no_samples: int, probability: float = None,
):
    """
    Get a sample of frames from a video file
    :param image_cache_dir:
    :param probability: (float) The probability of sampling a frame
    :param video_file:  (str) the video file name
    :param min_no_samples :  (int) the number of frames to sample (if there is no probability, otherwise ignored)
    :return:
    """
    frames_from_dir = read_frames_from_directory(image_cache_dir)
    frames_from_video_file = get_sample_of_frames_from_video_file(video_file, min_no_samples, probability,
                                                                  image_cache_dir)
    total = 0
    for frame_no, frame in frames_from_dir:
        print(f'Frame from directory: {frame_no}')
        yield frame_no, frame
        total += 1
    if total == 0:
        for frame_no, frame in frames_from_video_file:
            # print('Frame from video file: {frame_no}')
            yield frame_no, frame
            total += 1
    return total


def get_sample_of_frames_from_video_file(
        video_file: str, min_no_samples: int, probability: float = None,
        image_cache_dir: str = None
) -> Any:
    """
     Get a sample of frames from a video file
    :param probability: (float) The probability of sampling a frame
    :param video_file:  (str) the video file name
    :param min_no_samples :  (int) the number of frames to sample (if there is no probability, otherwise ignored)
    :return:
    """
    number_of_frames = get_number_frames(video_file)
    print(f'Length of video: {number_of_frames}')

    num_samples = min_no_samples
    if probability is not None:
        num_samples = max(int(probability * number_of_frames), num_samples)
    print(f'Number of samples: {num_samples}')

    with managed_cv2_open_file(video_file) as video:
        frames_to_pick = sorted(np.random.choice(number_of_frames, num_samples, replace=False))
        print(f'Random sample length: {len(frames_to_pick)}')
        print(f'Random sample: {frames_to_pick}')

        for frame_no in tqdm(frames_to_pick):
            ret, frame = read_frame_from_vid(video, frame_no)
            if not ret:
                break
            if image_cache_dir:
                new_suffix = f'{frame_no:06d}'
                new_path = create_new_filename_with_suffix(video_file, image_cache_dir, 'jpg', new_suffix)
                save_image(frame, str(new_path))
            yield frame_no, frame
        return None


def read_frames_from_directory(directory, img_format='jpg'):
    """
    Read frames from a directory
    :param directory:
    :param img_format:
    :return:
    """

    img_files = list(sorted(Path(directory).rglob(f'*.{img_format}')))
    # Create a regular expression to match the file names:
    regex = re.compile(r'(.*)__(\d+)')
    for img_file in img_files:
        if not img_file.is_file():
            continue
        match = regex.match(img_file.stem)
        if not match:
            continue
        # Parse the integer frame number from the file name regex pattern
        frame_no = int(int(match.group(2)))
        yield frame_no, load_image(str(img_file))


@contextmanager
def managed_cv2_open_file(*args, **kwds):
    # Code to acquire resource
    video_file_handler = cv2.VideoCapture(*args, **kwds)
    try:
        yield video_file_handler
    finally:
        # Code to release resource
        video_file_handler.release()


def create_mean_std_frames_incremental(all_frames, blur_radius: int = None):
    """
    Create mean and standard deviation frames incrementally
    Does not require all frames to be loaded into memory

    Uses an online algorithm for calculating variance, as seen in this example:
    https://math.stackexchange.com/a/102982

    By calculating the sum of the squares of the values, we can calculate the average and standard deviation incrementally
    This has the advantage of not requiring all the values to be stored in memory, and can be
    implemented using lazy-evaluation of the source (e.g. using a generator)
    Also, since the original values are bytes, the sum of squares will not overflow and the calculation can be
    done entirely in integer arithmetic up to the last stage requiring division.

    :param blur_radius:
    :param all_frames: Iterable of frames (must be of the same size)
    :return: mean_frame as uint8, std_frame as float32 divided by 255
    """
    T0 = 0
    T1 = 0
    T2 = 0

    for frame_no, frame in all_frames:
        if blur_radius:
            frame = cv2.GaussianBlur(frame, (blur_radius, blur_radius), 0)
        frame64 = frame.astype(np.uint64)
        if frame_no == 0:
            T0 = 1
            T1 = frame64
            T2 = (frame64 ** 2)
        else:
            T0 = T0 + 1
            T1 = T1 + frame64
            T2 = T2 + frame64 ** 2

    mean_frame = T1 / T0
    std_frame = np.sqrt(T0 * T2 - T1 * T1) / T0

    return mean_frame.astype(np.int8), std_frame / 255.0


def dilate_image(img, mask=(5, 5), iterations=1):
    kernel = np.ones(mask, np.uint8)
    img_dilated = cv2.dilate(img, kernel, iterations)
    return img_dilated


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
