import os

from django.http import HttpResponse, Http404, FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView

from app_video.models import Video
from .serializers import VideoSerializer




class VideoListView(generics.ListAPIView):
    queryset = Video.objects.all().order_by('-created_at')
    serializer_class = VideoSerializer


class VideoPlaylistView(APIView):

    def get(self, request, movie_id, resolution, file_name=None, is_playlist=False):
        video = get_object_or_404(Video, id=movie_id)

        if is_playlist:
            field_name = f"video_{resolution}"
            video_field = getattr(video, field_name, None)

            if not video_field or not video_field.name:
                raise Http404("Resolution not supported")

            file_path = video_field.path
            content_type = "application/vnd.apple.mpegurl"
        else:
            video_dir = os.path.dirname(video.video_file.path)
            file_path = os.path.join(video_dir, file_name)
            content_type = "video/MP2T"

        if not os.path.exists(file_path):
            raise Http404(f"File not found.")

        return FileResponse(open(file_path, 'rb'), content_type=content_type)
