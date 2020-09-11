from typing import Optional

import graphene
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import Activity, Badge, Course, Resource, School, Subject
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

    # Only return email if user is querying his own profile.
    def resolve_email(self, info: ResolveInfo) -> str:
        assert info.context is not None
        user = info.context.user

        if not user.is_anonymous and user.email == self.email:
            return self.email
        else:
            return ""

    def resolve_avatar(self, info: ResolveInfo) -> str:
        return self.avatar.url if self.avatar else ""

    def resolve_avatar_thumbnail(self, info: ResolveInfo) -> str:
        return self.avatar_thumbnail.url if self.avatar_thumbnail else ""

    # Only return verification status if user is querying his own profile.
    def resolve_verified(self, info: ResolveInfo) -> Optional[bool]:
        assert info.context is not None

        if self.pk == info.context.user.pk:
            return info.context.user.verified
        else:
            return None

    # Only return school if user is querying his own profile.
    def resolve_school(self, info: ResolveInfo) -> Optional["School"]:
        assert info.context is not None
        return self.school if self.pk == info.context.user.pk else None

    # Only return subject if user is querying his own profile.
    def resolve_subject(self, info: ResolveInfo) -> Optional["Subject"]:
        assert info.context is not None
        return self.subject if self.pk == info.context.user.pk else None

    # Only return starred courses if user is querying his own profile.
    def resolve_starred_courses(
        self, info: ResolveInfo
    ) -> Optional["QuerySet[Course]"]:
        assert info.context is not None
        if self.pk == info.context.user.pk:
            return Course.objects.filter(stars__user__pk=self.pk)
        else:
            return None

    # Only return starred resources if user is querying his own profile.
    def resolve_starred_resources(
        self, info: ResolveInfo
    ) -> Optional["QuerySet[Resource]"]:
        assert info.context is not None
        if self.pk == info.context.user.pk:
            return Resource.objects.filter(stars__user__pk=self.pk)
        else:
            return None

    def resolve_badges(self, info: ResolveInfo) -> "QuerySet[Badge]":
        return self.badges.all()

    # Only return activity if user is querying his own profile.
    def resolve_activity(self, info: ResolveInfo) -> Optional["QuerySet[Activity]"]:
        assert info.context is not None
        if self.pk == info.context.user.pk:
            return self.activity.all()
        else:
            return None
