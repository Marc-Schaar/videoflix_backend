import pytest

from django.contrib.auth import get_user_model


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="testmarc", email="marc@test.de", password="pasword1234"
    )
