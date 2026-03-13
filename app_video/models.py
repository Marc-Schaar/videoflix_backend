import os
from django.db import models
from django.http import Http404

"""Data model and helpers for application videos.

The :class:`Video` model stores metadata and multiple FileField references to
converted HLS playlists.  The module also defines helper functions for
constructing upload paths.
"""

VIDEO_RESOLUTIONS = {"480p": "hd480", "720p": "hd720", "1080p": "hd1080", "4k": "4k"}


def video_upload_path(instance, filename):
    """Return the storage path for a newly uploaded source video.

    Uploaded files are placed directly under ``videos/source/`` using their
    original filename.
    """
    return f"videos/source/{filename}"


def thumbnail_upload_path(instance, filename):
    """Return the path for storing generated thumbnails.

    Thumbnails live under ``videos/thumbnails/`` and keep the supplied filename
    (usually derived from the source video name).
    """
    return f"videos/thumbnails/{filename}"


class Video(models.Model):
    """Primary model representing an uploaded video.

    Fields for each resolution are populated asynchronously by background jobs
    after the initial upload.  ``thumbnail_url`` holds the generated image
    used across the frontend.
    """

    title = models.CharField(max_length=250, null=False, blank=False)
    description = models.TextField(max_length=1000, null=False, blank=False)
    category = models.CharField(max_length=250, null=False, blank=False)
    video_file = models.FileField(upload_to=video_upload_path)
    video_480p = models.FileField(upload_to=video_upload_path, null=True, blank=True)
    video_720p = models.FileField(upload_to=video_upload_path, null=True, blank=True)
    video_1080p = models.FileField(upload_to=video_upload_path, null=True, blank=True)
    video_4k = models.FileField(upload_to=video_upload_path, null=True, blank=True)
    thumbnail_url = models.ImageField(
        upload_to=thumbnail_upload_path, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_hls_playlist_path(self, resolution):
        """Return the filesystem path of an HLS playlist for ``resolution``.

        Raises ``Http404`` if the requested resolution is not available or if the
        underlying file cannot be found.  This is primarily used by the API
        views to forward requests to the correct media file.
        """

        field_name = f"video_{resolution}"
        video_field = getattr(self, field_name, None)

        if not video_field or not video_field.name:
            raise Http404(f"Resolution {resolution}is not supported.")

        if not os.path.exists(video_field.path):
            raise Http404("Playlist File is not found on Server")

        return video_field.path

    def get_hls_path(self, resolution, segment=None):
        """
        Return the absolute path to either a resolution-specific playlist or a segment.

        The method uses the resolution field to locate the corresponding directory
        (e.g., videos/{id}/{resolution}/). If a ``segment`` name is provided,
        it returns the path to that specific file within that directory.
        Otherwise, it returns the path to the HLS playlist (.m3u8).

        Raises:
            Http404: If the resolution is not supported or the file does not exist.
        """

        field_name = f"video_{resolution}"
        video_field = getattr(self, field_name, None)

        if not video_field or not video_field.name:
            raise Http404(f"Resolution {resolution} is not supported.")

        res_dir = os.path.dirname(video_field.path)

        if segment:
            path = os.path.join(res_dir, segment)
        else:
            path = video_field.path

        if not os.path.exists(path):
            raise Http404(f"File not found: {path}")

        return path
