import cv2
import matplotlib.pyplot as plt
from tqdm import tqdm

from utils import managed_cv2_open_file, read_frame_from_vid, frame_stream_sample_reader, \
    get_sample_of_frames_from_video_file
import random
import numpy as np

# for frame_no in range(int(length_frame / 10), int(length_frame), frame_step):
#     ret, frame = read_frame_from_vid(video, frame_no)
#     if not ret:
#         break
#     if blur_radius:
#         frame = cv2.GaussianBlur(frame, (blur_radius, blur_radius), 0)
#     yield frame


# video_file_name = r'C:\Users\Assaf\Dropbox\Program\VideoSamples\Nanny_Letterbox.mkv'
# video_file_name = r'Q:\MOVIES\Galaxy Quest_.mkv'
video_file_name = r'Q:\MOVIES\Murder on the Orient Express.mkv'


def create_mean_std_frames(all_frames):
    all_frames_expanded = [np.expand_dims(frame, axis=3) for frame in all_frames]
    all_frames_4d = np.concatenate(all_frames_expanded, axis=3)

    mean_frame = np.mean(all_frames_4d, axis=3)
    std_frame = np.std(all_frames_4d, axis=3)

    return mean_frame.astype(np.int8), std_frame / 255.0


def opencv_display_image(img, window_name='image'):
    cv2.imshow(window_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def mask_for_display(img_mask):
    return (255.0 * img_mask).astype(np.uint8)


def normalize_array(array):
    array_normalized = (array - np.min(array)) / (np.max(array) - np.min(array))
    return array_normalized


# itr = frame_stream_sample_reader(video_file_name, 100)
frame_samples = get_sample_of_frames_from_video_file(video_file_name, 20, 0.01, blur_radius=5)
# for i, x in frame_samples.items():
#     print('Frame: ', i, 'Mean: ', np.mean(x), 'Std: ', np.std(x))

mean_image, std_image = create_mean_std_frames(frame_samples.values())
opencv_display_image(mean_image)
std_values_1channel = np.abs(std_image).mean(axis=2)
# Normalize


std_normalized = std_values_1channel  # normalize_array(std_values_1channel)
std_normalized_mask = (std_normalized < 0.1)  # True/False Values
opencv_display_image((255.0 * std_normalized_mask.astype(np.float16)).astype(np.uint8))

for percentile in [10, 9, 8, 7, 6, 5]:
    std_normalized_mask = (std_normalized < np.percentile(std_values_1channel, percentile))
    opencv_display_image((255.0 * std_normalized_mask.astype(np.float16)).astype(np.uint8), f'Percentile: {percentile}')

print("Finished")
