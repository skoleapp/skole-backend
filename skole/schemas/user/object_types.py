from functools import wraps
from typing import Callable, Optional, TypeVar

import graphene
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from graphene_django import DjangoObjectType

from skole.models import Activity, Badge, Course, Resource, School, Subject, User
from skole.schemas.activity import ActivityObjectType
from skole.schemas.badge import BadgeObjectType
from skole.schemas.course import CourseObjectType
from skole.schemas.resource import ResourceObjectType
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


class UserObjectType(DjangoObjectType):
    email = graphene.String()
    score = graphene.Int()
    avatar = graphene.String()
    avatar_thumbnail = graphene.String()
    verified = graphene.Boolean()
    school = graphene.Field(SchoolObjectType)
    subject = graphene.Field(SubjectObjectType)
    rank = graphene.String()
    badges = graphene.List(BadgeObjectType)
    starred_courses = graphene.List(CourseObjectType)
    starred_resources = graphene.List(ResourceObjectType)
    activity = graphene.List(ActivityObjectType)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "score",
            "title",
            "bio",
            "avatar",
            "avatar_thumbnail",
            "created",
            "verified",
            "starred_courses",
            "starred_resources",
            "created_courses",
            "created_resources",
            "activity",
        )

    @staticmethod
    def resolve_badges(root: User, info: ResolveInfo) -> QuerySet[Badge]:
        return root.badges.all()

    @staticmethod
    def resolve_avatar(root: User, info: ResolveInfo) -> str:
        return root.avatar.url if root.avatar else ""

    @staticmethod
    def resolve_avatar_thumbnail(root: User, info: ResolveInfo) -> str:
        return root.avatar_thumbnail.url if root.avatar_thumbnail else ""

    @staticmethod
    @private_field
    def resolve_email(root: User, info: ResolveInfo) -> str:
        """Only return email if user is querying their own profile."""
        return root.email

    @staticmethod
    @private_field
    def resolve_verified(root: User, info: ResolveInfo) -> bool:
        """Only return verification status if user is querying their own profile."""
        return root.verified

    @staticmethod
    @private_field
    def resolve_school(root: User, info: ResolveInfo) -> Optional[School]:
        """Only return school if user is querying their own profile."""
        return root.school

    @staticmethod
    @private_field
    def resolve_subject(root: User, info: ResolveInfo) -> Optional[Subject]:
        """Only return subject if user is querying their own profile."""
        return root.subject

    @staticmethod
    @private_field
    def resolve_starred_courses(root: User, info: ResolveInfo) -> QuerySet[Course]:
        """Only return starred courses if user is querying their own profile."""
        return Course.objects.filter(stars__user__pk=root.pk)

    @staticmethod
    @private_field
    def resolve_starred_resources(root: User, info: ResolveInfo) -> QuerySet[Resource]:
        """Only return starred resources if user is querying their own profile."""
        return Resource.objects.filter(stars__user__pk=root.pk)

    @staticmethod
    @private_field
    def resolve_activity(root: User, info: ResolveInfo) -> QuerySet[Activity]:
        """Only return activity if user is querying their own profile."""
        return root.activity.all()
