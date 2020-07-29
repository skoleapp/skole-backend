"""This module contains all the custom type aliases that are used in the app."""
from typing import Literal, Union

from skole.models import Comment, Course, Resource, User

CommentableModel = Union[Comment, Course, Resource]
PaginableModel = Union[Course, Resource, User]
VotableModel = Union[Comment, Course, Resource]

CourseOrderingOption = Literal["name", "-name", "score", "-score"]

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
