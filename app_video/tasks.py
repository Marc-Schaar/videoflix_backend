import subprocess
import os
import shutil

def convert_video(instance, resolution): 
    resolutions = {
        "480p":  "hd480",
        "720p":  "hd720",
        "1080p": "hd1080",
        "4k":    "4k"
    }

    if resolution not in resolutions:
        return
    source_path = instance.video_file.path

    file_root, _ = os.path.splitext(source_path)
    new_file = f"{file_root}_{resolution}.mp4"

    cmd = [
        'ffmpeg', '-i', source_path, 
        '-s', resolutions[resolution],
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-y',
        new_file
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg Error: {e.stderr}")


def delete_video_directory(instance):
    """
    Deletes the entire directory containing the video, 
    thumbnails, and all converted versions.
    """
    if instance.video_file:
        file_path = instance.video_file.path
        directory_to_delete = os.path.dirname(os.path.dirname(file_path))

        if os.path.exists(directory_to_delete):
            try:
                shutil.rmtree(directory_to_delete)
            except Exception as e:
                print(f"Error deleting directory {directory_to_delete}: {e}")
