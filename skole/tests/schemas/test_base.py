import inspect

from skole.models import School
from skole.schemas import thread
from skole.schemas.resource import DeleteResourceMutation
from skole.schemas.school import SchoolObjectType


def test_skole_object_type_meta_dynamic_api_docs() -> None:
    # pylint: disable=protected-access

    # Test that mutation docs get generated correctly.
    description = DeleteResourceMutation._meta.description
    expected = inspect.cleandoc(
        """
        Delete a resource.

        Results are sorted by creation time.

        Only allowed for users that are the creators of the object.

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

        Only allowed for authenticated users.

        Results are paginated.
        """
    )
    assert description == expected

    # Test that object type docs get generated correctly.
    description = SchoolObjectType._meta.description
    assert description == inspect.cleandoc(School.__doc__ or "")
