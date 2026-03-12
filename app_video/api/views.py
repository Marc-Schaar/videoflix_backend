from django.http import FileResponse
from rest_framework import generics

from app_video.models import Video
from .serializers import VideoSerializer





class VideoListView(generics.ListAPIView):
    queryset = Video.objects.all().order_by('-created_at')
    serializer_class = VideoSerializer


class VideoPlaylistView(generics.RetrieveAPIView):
    queryset = Video.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'movie_id'

   
    def build_file_response(self, file_path, content_type):
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Cache-Control'] = 'public, max-age=3600'
        return response


    def retrieve(self, request, *args, **kwargs):
        video = self.get_object()
        resolution = self.kwargs.get('resolution')
        segment = kwargs.get('segment')

        file_path = video.get_hls_path(resolution, segment)
        content_type = "video/MP2T" if segment else "application/vnd.apple.mpegurl"

        return self.build_file_response(file_path, content_type)

   