import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db import transaction
from django.core.cache import cache

from .models import Video, VIDEO_RESOLUTIONS
from .tasks import convert_video, create_thumbnail, delete_video_files_task


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        cache.clear()
        transaction.on_commit(lambda: create_thumbnail.delay(instance.id))

        for res in VIDEO_RESOLUTIONS.keys():
            transaction.on_commit(lambda r=res: convert_video.delay(instance.id, r))


@receiver(post_delete, sender=Video)
def on_video_delete(sender, instance, **kwargs):
    paths = []
    if instance.video_file:
        paths.append(instance.video_file.path)
    if instance.thumbnail_url:
        paths.append(instance.thumbnail_url.path)


    delete_video_files_task.delay(paths, instance.id)
