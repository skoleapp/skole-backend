"""This module contains all the custom type aliases that are used in the app."""
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Union

if TYPE_CHECKING:  # pragma: no cover
    # To avoid circular import.
    from skole.models import Comment, Course, Resource, User  # noqa

CommentableModel = Union["Comment", "Course", "Resource"]
PaginableModel = Union["Course", "Resource", "User"]
VotableModel = Union["Comment", "Course", "Resource"]
StarrableModel = Union["Course", "Resource"]

CourseOrderingOption = Literal["best", "score", "name", "-name"]

ID = Union[str, int, None]
"""A type representing a GraphQL ID in Python code.

Variables with this type should not be used as normal string or integers.
Should not be confused with `graphene.ID()`.
Can also be a value that is used to query a Django model by its pk,
since e.g. `Foo.objects.get(pk=id)` works fine with integers and strings.

Examples:
    >>> var: ID = 0  # mypy: ok
    >>> var: ID = 123  # mypy: ok
    >>> var: ID = "0"  # mypy: ok
    >>> var: ID = "123"  # mypy: ok
    >>> var: ID = None  # mypy: ok
    >>> var: ID = ""  # mypy: ok, but probably should not be used
    >>> var: ID = -123  # mypy: ok, but should not be used
    >>> var: ID = graphene.ID()  # mypy: error!
    >>> var: ID = School()  # mypy: error!

"""

Fixture = Any
"""A type representing the return value of a pytest fixture.

Fixtures are just functions that are decorated with @pytest.fixture.
Using this as the type of a parameter makes its purpose immediately clear.

"""

JsonDict = Dict[str, Any]
"""A type representing a JSON object like dictionary.

Exactly the same as `mypy.types.JsonDict`, just defined here, to avoid having mypy
as a production dependency.
"""

AnyJson = Union[JsonDict, List[JsonDict]]
