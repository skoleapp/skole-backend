from typing import Optional

import graphene
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import Activity, Badge, Course, Resource, School, Subject, User
from skole.schemas.activity import ActivityObjectType
from skole.schemas.badge import BadgeObjectType
from skole.schemas.course import CourseObjectType
from skole.schemas.resource import ResourceObjectType
from skole.schemas.school import SchoolObjectType
from skole.schemas.subject import SubjectObjectType


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
    def resolve_email(root: User, info: ResolveInfo) -> str:
        """Only return email if user is querying his own profile."""
        assert info.context is not None
        user = info.context.user

        if not user.is_anonymous and user.email == root.email:
            return root.email
        else:
            return ""

    @staticmethod
    def resolve_avatar(root: User, info: ResolveInfo) -> str:
        return root.avatar.url if root.avatar else ""

    @staticmethod
    def resolve_avatar_thumbnail(root: User, info: ResolveInfo) -> str:
        return root.avatar_thumbnail.url if root.avatar_thumbnail else ""

    @staticmethod
    def resolve_verified(root: User, info: ResolveInfo) -> Optional[bool]:
        """Only return verification status if user is querying his own profile."""
        assert info.context is not None

        if root.pk == info.context.user.pk:
            return info.context.user.verified
        else:
            return None

    @staticmethod
    def resolve_school(root: User, info: ResolveInfo) -> Optional[School]:
        """Only return school if user is querying his own profile."""
        assert info.context is not None
        return root.school if root.pk == info.context.user.pk else None

    @staticmethod
    def resolve_subject(root: User, info: ResolveInfo) -> Optional[Subject]:
        """Only return subject if user is querying his own profile."""
        assert info.context is not None
        return root.subject if root.pk == info.context.user.pk else None

    @staticmethod
    def resolve_starred_courses(
        root: User, info: ResolveInfo
    ) -> Optional[QuerySet[Course]]:
        """Only return starred courses if user is querying his own profile."""
        assert info.context is not None
        if root.pk == info.context.user.pk:
            return Course.objects.filter(stars__user__pk=root.pk)
        else:
            return None

    @staticmethod
    def resolve_starred_resources(
        root: User, info: ResolveInfo
    ) -> Optional[QuerySet[Resource]]:
        """Only return starred resources if user is querying his own profile."""
        assert info.context is not None
        if root.pk == info.context.user.pk:
            return Resource.objects.filter(stars__user__pk=root.pk)
        else:
            return None

    @staticmethod
    def resolve_badges(root: User, info: ResolveInfo) -> QuerySet[Badge]:
        return root.badges.all()

    @staticmethod
    def resolve_activity(root: User, info: ResolveInfo) -> Optional[QuerySet[Activity]]:
        """Only return activity if user is querying his own profile."""
        assert info.context is not None
        if root.pk == info.context.user.pk:
            return root.activity.all()
        else:
            return None
