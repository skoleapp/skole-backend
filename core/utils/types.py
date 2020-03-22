from typing import Union

from core.models import Comment, Course, Resource, User

CommentableModel = Union[Comment, Course, Resource]
PaginableModel = Union[Course, Resource, User]
VotableModel = Union[Comment, Course, Resource]
