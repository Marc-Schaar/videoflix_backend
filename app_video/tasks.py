import os
import time
import logging
from django.core.files.base import ContentFile
from django_rq import job

from .models import VIDEO_RESOLUTIONS, Video
from .utils import (
    get_video_paths,
    run_ffmpeg,
    update_video_instance,
    delete_physical_file_by_path,
    delete_video_id_directory,
    remove_empty_none_dir,
)

logger = logging.getLogger(__name__)


@job
def convert_video(instance_id, resolution_key):
    time.sleep(1)
    try:
        instance = Video.objects.filter(pk=instance_id).first()
        if not instance:
            logger.warning(f"Video {instance_id} nicht gefunden. Task abgebrochen.")
            return
        ffmpeg_resolution = VIDEO_RESOLUTIONS.get(resolution_key)

        if not ffmpeg_resolution:
            return

        source, target = get_video_paths(instance, resolution_key)

        cmd = [
            "ffmpeg",
            "-i",
            source,
            "-s",
            ffmpeg_resolution,
            "-c:v",
            "libx264",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-hls_time",
            "10",
            "-hls_list_size",
            "0",
            "-f",
            "hls",
            "-y",
            target,
        ]

        if run_ffmpeg(cmd, f"Convert {resolution_key} to HLS"):
            update_video_instance(instance, f"video_{resolution_key}", target)
            remove_empty_none_dir()

    except Video.DoesNotExist:
        logger.error(f"Video with ID {instance_id} not found.")


@job
def create_thumbnail(instance_id):
    time.sleep(1)
    try:
        instance = Video.objects.filter(pk=instance_id).first()
        if not instance:
            logger.warning(
                f"Task abgebrochen: Video {instance_id} existiert nicht (mehr)."
            )
            return
        source, thumb_path = get_video_paths(instance)

        logger.info(f"Source: {source}")
        logger.info(f"Target Thumb: {thumb_path}")

        if not os.path.exists(source):
            logger.error(f"Quelldatei nicht gefunden: {source}")
            return

        cmd = [
            "ffmpeg",
            "-ss",
            "00:00:01",
            "-i",
            source,
            "-vframes",
            "1",
            "-q:v",
            "2",
            "-y",
            thumb_path,
        ]

        if run_ffmpeg(cmd, "Thumbnail"):
            if os.path.exists(thumb_path):
                with open(thumb_path, "rb") as f:
                    file_name = os.path.basename(thumb_path)
                    instance.thumbnail_url.save(
                        file_name, ContentFile(f.read()), save=True
                    )
                os.remove(thumb_path)
                logger.info(f"SUCCESS: Thumbnail für {instance.title} erstellt.")
            else:
                logger.error(
                    f"FFmpeg war erfolgreich, aber Datei fehlt unter: {thumb_path}"
                )

    except Exception as e:
        logger.error(f"Fehler beim Thumbnail: {e}", exc_info=True)


@job
def delete_video_files_task(paths_to_delete, video_id):
    """Background task to clean up files after a database record is gone."""
    for path in paths_to_delete:
        delete_physical_file_by_path(path)

    delete_video_id_directory(video_id)
