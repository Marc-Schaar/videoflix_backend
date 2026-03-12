import subprocess
import os
import shutil
import logging
from django.core.files.base import ContentFile
from django_rq import job


from .models import VIDEO_RESOLUTIONS, Video
from .utils import get_video_paths, run_ffmpeg, update_video_instance

logger = logging.getLogger(__name__)


@job
def convert_video(instance_id, resolution_key):
    try:
        instance = Video.objects.get(pk=instance_id)
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
            "-y",
            target,
        ]

        if run_ffmpeg(cmd, f"Convert {resolution_key}"):
            update_video_instance(instance, f"video_{resolution_key}", target)

    except Video.DoesNotExist:
        logger.error(f"Video with ID {instance_id} not found.")


@job
def create_thumbnail(instance_id):
    try:
        instance = Video.objects.get(pk=instance_id)
        source, thumb_path = get_video_paths(instance)

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

        if not os.path.exists(source):
            logger.error(f"Quelldatei nicht gefunden: {source}")
            return

        if run_ffmpeg(cmd, "Thumbnail"):
            with open(thumb_path, "rb") as f:
                instance.thumbnail_url.save(
                    f"thumb_{instance.id}.jpg", ContentFile(f.read()), save=False
                )
                instance.save(update_fields=["thumbnail_url"])
            os.remove(thumb_path)
            logger.info(f"SUCCESS: Thumbnail für {instance.title} erstellt.")

    except Video.DoesNotExist:
        logger.error(f"Video with ID {instance_id} not found.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during thumbnail creation: {e}")


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
                logger.error(f"Error deleting directory {directory_to_delete}: {e}")
