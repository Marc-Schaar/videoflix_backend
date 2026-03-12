import subprocess
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_video_paths(instance, resolution_key=None):
    source_path = instance.video_file.path
    file_root, _ = os.path.splitext(source_path)

    if resolution_key:
        new_file = f"{file_root}_{resolution_key}.mp4"
        return source_path, new_file

    thumb_path = f"{file_root}_thumb.jpg"
    return source_path, thumb_path


def run_ffmpeg(cmd, task_name):
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg {task_name} Error: {e.stderr}")
        return False


def update_video_instance(instance, field_name, file_path):
    if os.path.exists(file_path):
        rel_path = os.path.relpath(file_path, settings.MEDIA_ROOT).replace("\\", "/")
        setattr(instance, field_name, rel_path)
        instance.save(update_fields=[field_name])
        logger.info(f"DATABASE: {field_name} erfolgreich aktualisiert.")
