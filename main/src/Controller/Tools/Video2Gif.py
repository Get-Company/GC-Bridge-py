import os
import subprocess
from moviepy.editor import *


def make_gif(input_video, output_gif, width, start=None, end=None, lossy=90, colors=256):
    # Load the video using MoviePy
    video_clip = VideoFileClip(input_video)

    # Define the start and end time for the GI
    video_clip = video_clip.subclip(start, end)

    # Concatenate forward and backward
    video_clip = concatenate([video_clip, video_clip.fx(vfx.time_mirror)])

    # Define the desired width of the GIF
    width = min(width, video_clip.w)  # Don't upscale the video

    # Resize the video using MoviePy
    video_clip_resized = video_clip.resize(width=width)

    # Define the path for the temporary video file
    temp_video_file = os.path.splitext(output_gif)[0] + "_temp.gif"
    print("Temp File created:", temp_video_file)

    # Save the resized video as a temporary file
    video_clip_resized.write_gif(temp_video_file, fps=15, fuzz=2)

    # Define the options for Gifsicle
    options = ["-O3", "--lossy={}".format(lossy), "--colors={}".format(colors)]

    # Define the input and output files
    input_file = temp_video_file
    output_file = output_gif

    # Build the command to run Gifsicle
    command = ["gifsicle"] + options + ["--resize-width", str(width), "-i", input_file, "-o", output_file]

    # Run the command using subprocess
    subprocess.run(command, check=True)

    # Remove the temporary video file
    os.remove(temp_video_file)

    # Check if the output file was created
    if not os.path.isfile(output_file):
        raise RuntimeError("Failed to create output GIF file")

# make_gif(
#     input_video=r"D:\video\DaVinci\Classei\Produkte\Classata Schrank\Classata-Schrank 5-Schuebe V2-low.mp4",
#     output_gif=r"D:\video\DaVinci\Classei\Produkte\Classata Schrank\example_drawer_open.gif",
#     width=400,
#     start=7,
#     end=11,
#     lossy=90
# )

make_gif(
    input_video=r"D:\video\DaVinci\Classei\Produkte\Classata Schrank\Classata-Schrank 5-Schuebe V2-low.mp4",
    output_gif=r"D:\video\DaVinci\Classei\Produkte\Classata Schrank\zoom_to_drawer.gif",
    width=400,
    start=17,
    end=19,
    lossy=0
)

# make_gif(
#     input_video=r"D:\video\DaVinci\Classei\Produkte\Classata Schrank\Classata-Schrank 5-Schuebe V2-low.mp4",
#     output_gif=r"D:\video\DaVinci\Classei\Produkte\Classata Schrank\zoom_from_drawer.gif",
#     width=400,
#     start=39,
#     end=42,
#     lossy=90
# )
