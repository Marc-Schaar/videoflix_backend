import subprocess
import os
import logging
import shutil
from django.conf import settings

logger = logging.getLogger(__name__)

"""Utility functions shared between tasks, models and signals.

These helpers know how to construct paths inside ``MEDIA_ROOT``, invoke
ffmpeg, update model fields and perform filesystem cleanup.  They are kept
thin so that the business logic in tasks and signal handlers remains clean.
"""

def get_video_paths(instance, resolution_key=None):
    """Return filesystem paths for a video and its derived artifact.
    When ``resolution_key`` is omitted the function returns ``(source_path,
    thumbnail_path)`` where ``thumbnail_path`` will be placed under
    ``MEDIA_ROOT/videos/thumbnails``.  If a resolution is given the second
    element is the path to an HLS playlist file inside a subdirectory named
    after the instance ID and resolution (e.g. ``videos/42/720p/``).
    The function guarantees that the target directory exists before returning.
    """

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
    """Execute the given ``ffmpeg`` command and report success.

    The returned boolean indicates whether the invocation exited with a
    zero status code.  Any stderr output from ffmpeg is logged at ERROR level
    so that callers can diagnose failures.
    """

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg {task_name} Error: {e.stderr}")
        return False


def update_video_instance(instance, field_name, file_path):
    """Store the given ``file_path`` on the ``instance`` by updating the DB.

    The path is converted to a relative form against ``MEDIA_ROOT`` so that
    Django's storage system can resolve it later.  A queryset ``update`` is
    used to avoid re-saving the whole model instance, which is sufficient
    because only one field is changing.
    """

    if os.path.exists(file_path):
        rel_path = os.path.relpath(file_path, settings.MEDIA_ROOT).replace("\\", "/")

        from .models import Video

        Video.objects.filter(pk=instance.id).update(**{field_name: rel_path})

        logger.info(f"DATABASE: {field_name} succesfully updated (by Queryset-Update).")


def delete_physical_file_by_path(file_path):
    """Remove a file from disk given an absolute path.

    Logs success or failure.  No error is raised if the path does not exist.
    """

    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")


def remove_empty_none_dir():
    """Remove a stray ``None`` directory if Django accidentally creates one.

    Some operations can result in a folder named ``None`` under ``videos/``
    when a video ID is missing.  This helper deletes it to keep the media tree
    tidy.
    """

    none_dir = os.path.join(settings.MEDIA_ROOT, "videos", "None")
    if os.path.exists(none_dir):
        try:
            shutil.rmtree(none_dir)
            logger.info("Cleanup: Leeren 'None'-Ordner entfernt.")
        except Exception as e:
            logger.error(f"Fehler beim Löschen desNone-Ordners: {e}")


def delete_video_id_directory(video_id):
    """Delete the entire directory tree for a given video ID.

    The path ``MEDIA_ROOT/videos/<video_id>/`` is removed if it exists and the
    supplied ID is numeric.  Silent if the directory is already missing.
    """

    if video_id:
        dir_path = os.path.join(settings.MEDIA_ROOT, "videos", str(video_id))
        if os.path.exists(dir_path) and str(video_id).isdigit():
            try:
                shutil.rmtree(dir_path)
                logger.info(f"Kompletter Video-Ordner gelöscht: {dir_path}")
            except Exception as e:
                logger.error(f"Fehler beim Löschen des Video-Ordners {video_id}: {e}")
