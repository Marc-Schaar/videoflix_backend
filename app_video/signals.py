from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .models import Video, VIDEO_RESOLUTIONS
from .tasks import convert_video, create_thumbnail, delete_video_directory


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
      
        for res in VIDEO_RESOLUTIONS.keys():
            convert_video.delay(instance.id, res)

        create_thumbnail.delay(instance.id)


@receiver(post_delete, sender=Video)
def on_video_delete(sender, instance, **kwargs):
    delete_video_directory(instance)
