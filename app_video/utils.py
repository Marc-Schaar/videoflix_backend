import subprocess
import os
import logging
import shutil
from django.conf import settings

logger = logging.getLogger(__name__)


def get_video_paths(instance, resolution_key=None):
    source_path = instance.video_file.path
    video_id = instance.id

    if resolution_key:
        file_name = os.path.basename(source_path)
        file_root, _ = os.path.splitext(file_name)

        target_dir = os.path.join(
            settings.MEDIA_ROOT, "videos", str(video_id), resolution_key
        )
        os.makedirs(target_dir, exist_ok=True)

        target_path = os.path.join(target_dir, f"{file_root}_{resolution_key}.m3u8")
        return source_path, target_path

    video_filename = os.path.basename(source_path)
    thumb_filename = os.path.splitext(video_filename)[0] + "_thumb.jpg"
    thumb_dir = os.path.join(settings.MEDIA_ROOT, "videos", "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)

    thumb_path = os.path.join(thumb_dir, thumb_filename)

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

        from .models import Video

        Video.objects.filter(pk=instance.id).update(**{field_name: rel_path})

        logger.info(f"DATABASE: {field_name} succesfully updated (by Queryset-Update).")


def delete_physical_file_by_path(file_path):
    """Löscht eine Datei anhand ihres Pfades."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")


def remove_empty_none_dir():
    """Löscht den 'None'-Ordner, falls Django ihn fälschlicherweise erstellt hat."""
    none_dir = os.path.join(settings.MEDIA_ROOT, "videos", "None")
    if os.path.exists(none_dir):
        try:
            shutil.rmtree(none_dir)
            logger.info("Cleanup: Leeren 'None'-Ordner entfernt.")
        except Exception as e:
            logger.error(f"Fehler beim Löschen des None-Ordners: {e}")


def delete_video_id_directory(video_id):
    """Löscht den kompletten Ordner eines spezifischen Videos (z.B. videos/42/)."""
    if video_id:
        dir_path = os.path.join(settings.MEDIA_ROOT, "videos", str(video_id))
        if os.path.exists(dir_path) and str(video_id).isdigit():
            try:
                shutil.rmtree(dir_path)
                logger.info(f"Kompletter Video-Ordner gelöscht: {dir_path}")
            except Exception as e:
                logger.error(f"Fehler beim Löschen des Video-Ordners {video_id}: {e}")
