from rest_framework import serializers
from app_video.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for the :class:`Video` model.

    Exposes only the subset of fields required by the frontend listing view.  The
    playlist and segment URLs are constructed client-side using these values.
    """

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "category",
            "description",
            "created_at",
            "thumbnail_url",
        ]
