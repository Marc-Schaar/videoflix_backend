from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .models import Video, VIDEO_RESOLUTIONS
from .tasks import convert_video, create_thumbnail, delete_video_directory


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        create_thumbnail.delay(instance.id)
        for res in VIDEO_RESOLUTIONS.keys():
            print(f"New video detected: {instance.title}. Processing resolutions...")
            convert_video.delay(instance.id, res)
        print("All conversions completed successfully.")


@receiver(post_delete, sender=Video)
def on_video_delete(sender, instance, **kwargs):
    delete_video_directory(instance)
