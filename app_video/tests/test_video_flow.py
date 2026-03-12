import os
import pytest
from app_video.models import VIDEO_RESOLUTIONS


@pytest.mark.django_db
def test_video_creation_and_conversion(video_instance, fake_run_ffmpeg):
    """Check that thumbnail and HLS files exist after creation."""

    video = video_instance()
    video.refresh_from_db()

    assert video.thumbnail_url, "Thumbnail Feld wurde nicht gefüllt"
    assert os.path.exists(video.thumbnail_url.path)

    for res in VIDEO_RESOLUTIONS.keys():
        field = getattr(video, f"video_{res}")
        assert field and field.name, f"Feld für {res} ist leer"
        assert os.path.exists(field.path), f"Datei für {res} wurde nicht physisch erstellt"


@pytest.mark.django_db
def test_video_path_helpers(video_instance, fake_run_ffmpeg):
    """Check the HLS path helper methods for playlists and segments."""
    video = video_instance()
    video.refresh_from_db()

    playlist_path = video.get_hls_path("480p")
    assert os.path.exists(playlist_path)
    assert playlist_path.endswith(".m3u8")

    video_dir = os.path.dirname(video.video_file.path)
    dummy_segment = "data01.ts"
    seg_full_path = os.path.join(video_dir, dummy_segment)

    with open(seg_full_path, "wb") as f:
        f.write(b"fake segment data")

    assert video.get_hls_path("480p", dummy_segment) == seg_full_path


@pytest.mark.django_db
def test_video_deletion_cleanup(video_instance, fake_run_ffmpeg):
    """Check that all associated files are removed from disk after deletion."""

    video = video_instance()
    video.refresh_from_db()

    paths_to_check = [video.video_file.path, video.thumbnail_url.path]
    for res in VIDEO_RESOLUTIONS.keys():
        paths_to_check.append(getattr(video, f"video_{res}").path)

    for p in paths_to_check:
        assert os.path.exists(p)

    video.delete()

    for p in paths_to_check:
        assert not os.path.exists(p), f"Datei {p} wurde nicht gelöscht!"
