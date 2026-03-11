import subprocess
import os


def convert_video(source, resolution):
    resolutions = {
        "480p":  "hd480",
        "720p":  "hd720",
        "1080p": "hd1080",
        "4k":    "4k"
    }

    if resolution not in resolutions:
        print(f"Auflösung {resolution} wird nicht unterstützt.")
        return

    file_root, _ = os.path.splitext(source)
    new_file = f"{file_root}_{resolution}.mp4"

    cmd = [
        'ffmpeg', '-i', source,
        '-s', resolutions[resolution],
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-y', 
        new_file
    ]

    try:
        print(f"Konvertiere zu {resolution}...")
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Fertig: {new_file}")
    except subprocess.CalledProcessError as e:
        print(f"Fehler: {e.stderr}")
