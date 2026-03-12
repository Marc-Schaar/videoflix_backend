from rest_framework import serializers
from app_video.models import Video


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'created_at',
            'video_file', 'thumbnail_url',
            'video_480p', 'video_720p', 'video_1080p', 'video_4k'
        ]
