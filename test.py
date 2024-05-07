import numpy as np
from inpaint import inpaint_image
from utils import *

temp_data_dir = './temp_data'

# video_file_name = r'C:\Users\Assaf\Dropbox\Program\VideoSamples\Nanny_Letterbox.mkv'
# video_file_name = r'Q:\MOVIES\Murder on the Orient Express.mkv'
# video_file_name = r'S:\TV Shows\פאזל\פאזל עונה 1 - פרק 6 - המקום הקבוע - video Dailymotion.mp4'
video_file_name = r'Q:\MOVIES\Galaxy Quest_.mkv'


def mask_for_display(img_mask):
    return (255.0 * img_mask).astype(np.uint8)


# save_sample_of_frames_from_video_file(temp_data_dir, video_file_name, 20, 0.01, 5)


# frame_samples = read_frames_from_directory(temp_data_dir)
# if (frame_samples is None):
#     print("No samples found")
#     exit(0)
#
# frame_samples = get_sample_of_frames_from_video_file(video_file_name, 200, 0.01, blur_radius=9)

# Normalize

mask_file_name = create_new_filename_with_suffix(video_file_name, temp_data_dir, 'png', 'mask')
if Path(mask_file_name).exists():
    mask = load_image(mask_file_name)
else:
    frame_samples = get_sample_of_frames_from_directory_or_video_file(temp_data_dir, video_file_name, 200, 0.05)
    mean_image, std_image = create_mean_std_frames_incremental(frame_samples, blur_radius=9)
    opencv_display_image(mean_image)
    std_values_1channel = np.abs(std_image).mean(axis=2)
    std_normalized = std_values_1channel  # normalize_array(std_values_1channel)
    std_normalized_mask = (std_normalized < 0.1)  # True/False Values
    std_mask_for_display = (255.0 * std_normalized_mask.astype(np.float16)).astype(np.uint8)
    # Taking a matrix of size 5 as the kernel

    # opencv_display_image(std_mask_for_display, 'Mask for display')
    mask = dilate_image(std_mask_for_display)
    save_image(mask, str(mask_file_name), 'png')
opencv_display_image(mask, 'Mask')
#
# # file_to_heal = r'temp_data/פאזל עונה 1 - פרק 6 - המקום הקבוע - video Dailymotion__035797.jpg'
# file_to_heal = r'temp_data/פאזל עונה 1 - פרק 6 - המקום הקבוע - video Dailymotion__034942.jpg'
# file_to_heal = r'temp_data/Galaxy Quest___095439.jpg'
# file_to_heal = r'temp_data/Galaxy Quest___101641.jpg'
file_to_heal = r'temp_data/Galaxy Quest___104249.jpg'


def heal_image_file(input_file, mask_file, output_dir):
    output_file_name = create_new_filename_with_suffix(input_file, output_dir, 'jpg', 'healed')
    output_image = inpaint_image(input_file, mask_file, output_file_name)
    return output_file_name, output_image


healed_file, healed_image = heal_image_file(file_to_heal, mask_file_name, temp_data_dir)
# healed_image = load_image(healed_file)
opencv_display_image(healed_image, 'Healed Image')
# two_images = cv2.hconcat([image, mask, healed_image])
#
# opencv_display_image(two_images, 'Healed Image')


print("Finished")
