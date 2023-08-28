import cv2

from utils import managed_cv2_open_file, read_frame_from_vid, frame_stream_sample_reader
import random

# for frame_no in range(int(length_frame / 10), int(length_frame), frame_step):
#     ret, frame = read_frame_from_vid(video, frame_no)
#     if not ret:
#         break
#     if blur_radius:
#         frame = cv2.GaussianBlur(frame, (blur_radius, blur_radius), 0)
#     yield frame


video_file_name = r'C:\Users\Assaf\Dropbox\Program\VideoSamples\Nanny_Letterbox.mkv'

itr = frame_stream_sample_reader(video_file_name, 100)
for i, x in enumerate(itr):
    print(x)
    print(i)
