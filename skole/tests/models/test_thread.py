import pytest

from skole.models import Thread


@pytest.mark.django_db
def test_str() -> None:
    thread1 = Thread.objects.get(pk=1)
    assert str(thread1) == "Test Thread 1"

    thread2 = Thread.objects.get(pk=2)
    assert str(thread2) == "Test Thread 2"

    thread3 = Thread.objects.get(pk=3)
    assert str(thread3) == "Test Thread 3"
