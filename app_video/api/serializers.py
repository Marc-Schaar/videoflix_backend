from rest_framework import serializers
from app_video.models import Video


class VideoSerializer(serializers.ModelSerializer):
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
