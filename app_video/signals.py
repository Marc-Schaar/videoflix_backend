import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .models import Video
from .tasks import convert_video, delete_video_directory


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        resolutions = ['480p', '720p', '1080p', '4k']

        for res in resolutions:
            print(f"New video detected: {instance.title}. Processing resolutions...")
            convert_video(instance, res)

        print('All conversions completed successfully.')


@receiver(post_delete, sender=Video)
def on_video_delete(sender, instance, **kwargs):
    delete_video_directory(instance)
