from functools import wraps
from typing import Callable, Optional, TypeVar

import graphene
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from skole.models import Badge, School, Subject, User
from skole.schemas.badge import BadgeObjectType
from skole.schemas.base import SkoleDjangoObjectType
from skole.schemas.school import SchoolObjectType
from skole.schemas.subject import SubjectObjectType
from skole.types import ResolveInfo

T = TypeVar("T")
UserResolver = Callable[[User, ResolveInfo], T]


def private_field(func: UserResolver[T]) -> UserResolver[Optional[T]]:
    """Use as a decorator to only return the field's value if it's the user's own."""

    @wraps(func)
    def wrapper(root: User, info: ResolveInfo) -> Optional[T]:
        if info.context.user.is_authenticated and root.pk == info.context.user.pk:
            return func(root, info)
        else:
            return None

    return wrapper


class UserObjectType(SkoleDjangoObjectType):
    """
    The following fields are private, meaning they are returned only if the user is
    querying one's own profile: `email`, `verified`, `school`, `subject`.

    For instances that are not the user's own user profile, these fields will return a
    `null` value.
    """

    slug = graphene.String()
    email = graphene.String()
    score = graphene.Int()
    avatar = graphene.String()
    avatar_thumbnail = graphene.String()
    verified = graphene.Boolean()
    school = graphene.Field(SchoolObjectType)
    subject = graphene.Field(SubjectObjectType)
    rank = graphene.String()
    badges = graphene.List(BadgeObjectType)
    unread_activity_count = graphene.Int()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "slug",
            "username",
            "email",
            "score",
            "title",
            "bio",
            "avatar",
            "avatar_thumbnail",
            "created",
            "verified",
            "unread_activity_count",
        )

    @staticmethod
    def resolve_badges(root: User, info: ResolveInfo) -> QuerySet[Badge]:
        return root.badges.order_by("pk")

    @staticmethod
    def resolve_avatar(root: User, info: ResolveInfo) -> str:
        return root.avatar.url if root.avatar else ""

    @staticmethod
    def resolve_avatar_thumbnail(root: User, info: ResolveInfo) -> str:
        return root.avatar_thumbnail.url if root.avatar_thumbnail else ""

    @staticmethod
    @private_field
    def resolve_email(root: User, info: ResolveInfo) -> str:
        return root.email

    @staticmethod
    @private_field
    def resolve_verified(root: User, info: ResolveInfo) -> bool:
        return root.verified

    @staticmethod
    @private_field
    def resolve_school(root: User, info: ResolveInfo) -> Optional[School]:
        return root.school

    @staticmethod
    @private_field
    def resolve_subject(root: User, info: ResolveInfo) -> Optional[Subject]:
        return root.subject

    @staticmethod
    @private_field
    def resolve_unread_activity_count(root: User, info: ResolveInfo) -> int:
        return root.activities.filter(read=False).order_by().count()
