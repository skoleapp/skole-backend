"""This module contains all the custom type aliases that are used in the app."""
from typing import TYPE_CHECKING, Any, Literal, TypedDict, Union

if TYPE_CHECKING:  # pragma: no cover
    from skole.models import Activity, Comment, Thread, User  # noqa: F401

CommentableModel = Union["Comment", "Thread"]
PaginableModel = Union["Thread", "User", "Activity", "Comment"]
VotableModel = Union["Comment", "Thread"]

ThreadOrderingOption = Literal["best", "score", "name", "-name"]

ID = Union[str, int, None]
"""
A type representing a GraphQL ID in Python code.

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
    >>> var: ID = ""  # mypy: ok, but should not be used!
    >>> var: ID = -123  # mypy: ok, but should not be used!
    >>> var: ID = graphene.ID()  # mypy: error!

"""

Fixture = Any
"""
A type representing the return value of a pytest fixture.

Fixtures are just functions that are decorated with @pytest.fixture.
Using this as the type of a parameter makes its purpose immediately clear.
"""

JsonDict = dict[str, Any]
"""
A type representing a JSON object like dictionary.

Exactly the same as `mypy.types.JsonDict`, just defined here, to avoid having mypy
as a production dependency.
"""

JsonList = list[JsonDict]
"""A type representing a list of JSON object like dictionaries."""

AnyJson = Union[JsonDict, JsonList]


class _FormErrorDict(TypedDict):
    field: str
    messages: list[str]


FormError = list[_FormErrorDict]
