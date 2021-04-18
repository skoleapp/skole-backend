import pytest

from skole.models import Comment


@pytest.mark.django_db
def test_str() -> None:
    comment1 = Comment.objects.get(pk=1)
    assert str(comment1) == "testuser2: Comment 1 to a thread."

    comment2 = Comment.objects.get(pk=2)
    assert str(comment2) == "testuser3: Comment 2 to a thread."

    comment22 = Comment.objects.get(pk=22)
    assert str(comment22) == "Anonymous Student: An anonymous comment to a thread."
