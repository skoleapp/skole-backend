from __future__ import annotations

import inspect

from skole.models import Badge
from skole.schemas import thread
from skole.schemas.badge import BadgeObjectType
from skole.schemas.comment import CreateCommentMutation


def test_skole_object_type_meta_dynamic_api_docs() -> None:
    # pylint: disable=protected-access

    # Test that mutation docs get generated correctly.
    description = CreateCommentMutation._meta.description
    expected = inspect.cleandoc(
        """
        Create a new comment.

        Attachments are popped of for unauthenticated users. The `user` field must match
        with the ID of the user making the query to save the user making the query as the
        author of the comment. This way even authenticated users can create anonymous
        comments by setting the `user` field as `null`.

        Only allowed for authenticated users that have verified their accounts.
        """
    )
    assert description == expected

    # Test that query resolver docs get generated correctly.
    description = thread.Query.starred_threads.description
    expected = inspect.cleandoc(
        """
        Return starred threads of the user making the query.

        Results are sorted by creation time. Return an empty list for unauthenticated
        users.

        Only allowed for authenticated users that have verified their accounts.

        Results are paginated.
        """
    )
    assert description == expected

    # Test that object type docs get generated correctly.
    description = BadgeObjectType._meta.description
    assert description == inspect.cleandoc(Badge.__doc__ or "")
