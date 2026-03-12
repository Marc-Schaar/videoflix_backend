from django.urls import path

from .views import VideoListView, VideoPlaylistView

"""URL configuration for the video API.

The module defines three routes:

* ``/video/`` – list all videos
* ``/video/<id>/<resolution>/index.m3u8`` – return playlist for given video
* ``/video/<id>/<resolution>/<segment>`` – stream individual HLS segments

Each pattern delegates to :class:`VideoListView` or :class:`VideoPlaylistView`.
"""

urlpatterns = [
    path("video/", VideoListView.as_view(), name="video-list"),
    path(
        "video/<int:movie_id>/<str:resolution>/index.m3u8",
        VideoPlaylistView.as_view(),
        name="video-playlist",
    ),
    path(
        "video/<int:movie_id>/<str:resolution>/<str:segment>",
        VideoPlaylistView.as_view(),
        name="video-segment",
    ),
]
