import uuid
import os
from django.db import models
from django.http import Http404

VIDEO_RESOLUTIONS = {"480p": "hd480", "720p": "hd720", "1080p": "hd1080", "4k": "4k"}


def video_upload_path(instance, filename):
    ext = filename.split(".")[-1].lower()
    folder_name = str(instance.id)

    if ext.lower() in ["jpg", "jpeg", "png", "webp"]:
        subfolder = "thumbnails"
    else:
        subfolder = "source"

    return f"videos/{folder_name}/{subfolder}/{filename}"


class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250, null=False, blank=False)
    description = models.TextField(max_length=1000, null=False, blank=False)
    category = models.CharField(max_length=250, null=False, blank=False)
    video_file = models.FileField(upload_to=video_upload_path)
    video_480p = models.FileField(upload_to=video_upload_path, null=True, blank=True)
    video_720p = models.FileField(upload_to=video_upload_path, null=True, blank=True)
    video_1080p = models.FileField(upload_to=video_upload_path, null=True, blank=True)
    video_4k = models.FileField(upload_to=video_upload_path, null=True, blank=True)
    thumbnail_url = models.ImageField(
        upload_to=video_upload_path, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def get_hls_playlist_path(self, resolution):
        field_name = f"video_{resolution}"
        video_field = getattr(self, field_name, None)

        if not video_field or not video_field.name:
            raise Http404(f"Auflösung {resolution} wird nicht unterstützt.")

        if not os.path.exists(video_field.path):
            raise Http404("Playlist-Datei wurde auf dem Server nicht gefunden.")

        return video_field.path

    def get_hls_path(self, resolution, segment=None):
        if segment:
            video_dir = os.path.dirname(self.video_file.path)
            path = os.path.join(video_dir, segment)
        else:
            field_name = f"video_{resolution}"
            video_field = getattr(self, field_name, None)
            if not video_field or not video_field.name:
                raise Http404("Auflösung nicht unterstützt.")
            path = video_field.path

        if not os.path.exists(path):
            raise Http404("Datei nicht gefunden.")
        return path
