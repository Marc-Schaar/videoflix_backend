from django.urls import path

from .views import VideoListView, VideoPlaylistView

urlpatterns = [
    path("video/", VideoListView.as_view(), name="video-list"),
    path("video/<uuid:movie_id>/<str:resolution>/index.m3u8",
         VideoPlaylistView.as_view(),
         {"is_playlist": True}, 
         name="video-playlist"),

    path("video/<uuid:movie_id>/<str:resolution>/<str:file_name>",
         VideoPlaylistView.as_view(),
         {"is_playlist": False},
         name="video-segments"),]
