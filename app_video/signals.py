from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db import transaction
from django.core.cache import cache

"""Signal handlers for Video model events.

This module connects the Video model to background tasks that perform
conversion, thumbnail creation and cleanup when records are created or
deleted. The handlers make use of Django's signal framework and take care of
clearing caches and scheduling jobs intelligently.
"""

from .models import Video, VIDEO_RESOLUTIONS
from .tasks import convert_video, create_thumbnail, delete_video_files_task


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """Kick off processing when a new **Video** instance is saved.

    Once the object has been created the cache is cleared and two types of
    jobs are queued via ``transaction.on_commit``:

    * ``create_thumbnail`` to extract a thumbnail image
    * ``convert_video`` for each of the configured resolutions

    Using ``on_commit`` guarantees the tasks only run after the database
    transaction has successfully committed, avoiding race conditions during
    tests or bulk imports.
    """

    if created:
        cache.clear()
        transaction.on_commit(lambda: create_thumbnail.delay(instance.id))

        for res in VIDEO_RESOLUTIONS.keys():
            transaction.on_commit(lambda r=res: convert_video.delay(instance.id, r))


@receiver(post_delete, sender=Video)
def on_video_delete(sender, instance, **kwargs):
    """Handle cleanup after a **Video** record is removed.

    The handler gathers the filesystem paths of the source video and its
    thumbnail (if they exist) and schedules ``delete_video_files_task`` to
    remove those files along with the directory for the given video ID.  This
    work is delegated to a background job to keep the deletion fast and
    non-blocking.
    """

    paths = []
    if instance.video_file:
        paths.append(instance.video_file.path)
    if instance.thumbnail_url:
        paths.append(instance.thumbnail_url.path)

    delete_video_files_task.delay(paths, instance.id)
