from rest_framework import generics
from app_video.models import Video
from .serializers import VideoSerializer




class VideoListView(generics.ListAPIView):
    queryset = Video.objects.all().order_by('-created_at')
    serializer_class = VideoSerializer
    
