from skole.models import Comment
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    comment1 = Comment.objects.get(pk=1)
    assert str(comment1) == "Starting comment for the thread on a res..."

    comment2 = Comment.objects.get(pk=2)
    assert str(comment2) == "Second comment of the thread."

    comment3 = Comment.objects.get(pk=3)
    assert str(comment3) == "Attachment Comment: 3"
