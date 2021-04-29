from __future__ import annotations

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

from skole.models import Thread


@pytest.mark.django_db
def test_str() -> None:
    thread1 = Thread.objects.get(pk=1)
    assert str(thread1) == "Test Thread 1"

    thread2 = Thread.objects.get(pk=2)
    assert str(thread2) == "Test Thread 2"

    thread3 = Thread.objects.get(pk=3)
    assert str(thread3) == "Test Thread 3"


@pytest.mark.django_db
def test_increment_views() -> None:
    thread = Thread.objects.get(pk=2)
    assert thread.views == 0

    request = HttpRequest()
    request.user = AnonymousUser()

    thread.increment_views(request)
    thread.increment_views(request)
    thread.increment_views(request)
    thread.refresh_from_db()
    assert thread.views == 3

    assert thread.user
    request.user = thread.user
    thread.increment_views(request)
    thread.refresh_from_db()
    assert thread.views == 3
