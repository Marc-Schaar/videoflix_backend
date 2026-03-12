import os
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from app_video.tasks import create_thumbnail, convert_video


@pytest.fixture(autouse=True)
def media_root(tmp_path, settings):
    """Isolate media files in a temporary directory for every test."""
    settings.MEDIA_ROOT = tmp_path / "media"
    return settings.MEDIA_ROOT


@pytest.fixture
def fake_run_ffmpeg(monkeypatch):
    """Stub out :func:`app_video.utils.run_ffmpeg` so that it always succeeds
    and creates a dummy file at the requested target path.

    This lets the conversion/thumbnail tasks exercise their logic without
    invoking the real ffmpeg binary.
    """

    def _fake(cmd, task_name):
        # assume last element of the command is the output path
        target = cmd[-1]
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as f:
            f.write(b"fake")
        return True

    # patch both the utility function and the copy imported into tasks
    monkeypatch.setattr("app_video.utils.run_ffmpeg", _fake)
    monkeypatch.setattr("app_video.tasks.run_ffmpeg", _fake)
    return _fake


@pytest.fixture(autouse=True)
def immediate_on_commit(monkeypatch):
    """Run any callbacks passed to ``transaction.on_commit`` right away.

    The signal handlers use ``transaction.on_commit`` to queue RQ jobs.  In
    tests the database is wrapped in a transaction that is eventually rolled
    back, so the callbacks would otherwise never execute.  By replacing the
    helper we ensure the tasks are scheduled immediately.
    """

    import django.db.transaction as django_transaction

    monkeypatch.setattr(django_transaction, "on_commit", lambda func: func())


@pytest.fixture(autouse=True)
def sync_rq(monkeypatch):
    """Make RQ jobs run synchronously by replacing ``.delay`` with a direct
    call.  The signals in :mod:`app_video.signals` use ``delay`` so this
    fixture is required to execute the tasks during model save/delete.
    """

    monkeypatch.setattr(create_thumbnail, "delay", lambda instance_id: create_thumbnail(instance_id))
    monkeypatch.setattr(convert_video, "delay", lambda instance_id, res: convert_video(instance_id, res))


@pytest.fixture
def make_video_file(tmp_path):
    """Return a helper that writes a small dummy file and returns its path."""

    def _make(name="video.mp4", content=b"dummy"):
        path = tmp_path / name
        path.write_bytes(content)
        return path

    return _make


@pytest.fixture
def video_instance(make_video_file):
    """Create and return a fresh :class:`~app_video.models.Video`.

    The instance is saved to the database and its ``video_file`` field will
    point to an actual file on disk inside ``MEDIA_ROOT``.
    """

    def _create():
        file_path = make_video_file()
        with open(file_path, "rb") as f:
            upfile = SimpleUploadedFile(file_path.name, f.read())

        # import inside function to avoid Django model import issues during
        # test collection
        from app_video.models import Video

        video = Video.objects.create(
            title="Test",
            description="desc",
            category="cat",
            video_file=upfile,
        )
        return video

    return _create
