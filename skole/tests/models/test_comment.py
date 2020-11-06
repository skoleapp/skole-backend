from skole.models import Comment
from skole.types import Fixture


def test_str(db: Fixture) -> None:
    comment1 = Comment.objects.get(pk=1)
    assert str(comment1) == "Comment 1 to a resource."

    comment2 = Comment.objects.get(pk=2)
    assert str(comment2) == "Comment 2 to a resource."
