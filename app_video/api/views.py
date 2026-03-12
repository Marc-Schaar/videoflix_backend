from django.http import FileResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import generics
from app_video.models import Video
from .serializers import VideoSerializer


class VideoListView(generics.ListAPIView):
    """API endpoint returning a paginated list of videos.

    Results are ordered by creation date (newest first) and are cached for
    fifteen minutes to reduce database load.
    """

    queryset = Video.objects.all().order_by("-created_at")
    serializer_class = VideoSerializer

    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class VideoPlaylistView(generics.RetrieveAPIView):
    """Serves HLS playlists and segments for a single video.

    The view is addressed as ``/video/<id>/<resolution>/...``.  A request with
    no ``segment`` argument returns the m3u8 playlist, while providing a
    segment name streams the corresponding transport stream chunk.
    """

    queryset = Video.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "movie_id"

    def build_file_response(self, file_path, content_type):
        """Wrap the given file path in a streaming ``FileResponse``.

        The response includes a one‑hour public cache header so that proxies and
        players can avoid re‑requesting the same segment repeatedly.
        """
        response = FileResponse(open(file_path, "rb"), content_type=content_type)
        response["Cache-Control"] = "public, max-age=3600"
        return response

    def retrieve(self, request, *args, **kwargs):
        """Handle the GET request by resolving the requested media file.

        The method extracts the resolution and optional segment from the URL,
        obtains the absolute path via :meth:`Video.get_hls_path`, selects the
        correct MIME type, and delegates to :meth:`build_file_response`.
        """
        video = self.get_object()
        resolution = self.kwargs.get("resolution")
        segment = kwargs.get("segment")

        file_path = video.get_hls_path(resolution, segment)
        content_type = "video/MP2T" if segment else "application/vnd.apple.mpegurl"

        return self.build_file_response(file_path, content_type)
