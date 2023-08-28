from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.config import change_settings


def clip_video_file(input_file, output_file, start_time, end_time):
    # Create code to clip a video file from start_time to end_time and output them to a different file (with the same codec)
    # input_file: the input video file  (string)
    # output_file: the output video file (string)
    # start_time: the start time of the clip (float)
    # end_time: the end time of the clip (float)
    clip = VideoFileClip(input_file).subclip(start_time, end_time)
    clip.write_videofile(output_file, codec='h264', audio_codec='mp3')


# change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})
clip_video_file(r"E:\Snl S14e17 Dolly Parton 06 Dolly Stories (Fixed Deint) 2X-600kbps.mkv",
                r"E:\Snl S14e17 Dolly Parton 06 Dolly Stories (Fixed Deint) 2X-600kbps_clip.mkv",
                15, 20)
