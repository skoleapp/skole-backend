from typing import Optional, cast

import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from graphql_jwt.decorators import login_required

from skole.models import Course, Resource, User
from skole.schemas.course import PaginatedCourseObjectType
from skole.schemas.resource import PaginatedResourceObjectType
from skole.types import ID, ResolveInfo
from skole.utils.api_descriptions import APIDescriptions
from skole.utils.pagination import get_paginator

from .object_types import UserObjectType


class Query(graphene.ObjectType):
    user_me = graphene.Field(UserObjectType, description=APIDescriptions.USER_ME,)

    user = graphene.Field(
        UserObjectType, id=graphene.ID(), description=APIDescriptions.USER,
    )

    created_courses = graphene.Field(
        PaginatedCourseObjectType,
        user=graphene.ID(),
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
        description=APIDescriptions.CREATED_COURSES,
    )

    created_resources = graphene.Field(
        PaginatedResourceObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
        description=APIDescriptions.CREATED_RESOURCES,
    )

    starred_courses = graphene.Field(
        PaginatedCourseObjectType,
        user=graphene.ID(),
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
        description=APIDescriptions.STARRED_COURSES,
    )

    starred_resources = graphene.Field(
        PaginatedResourceObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        ordering=graphene.String(),
        description=APIDescriptions.STARRED_RESOURCES,
    )

    @staticmethod
    @login_required
    def resolve_user_me(root: None, info: ResolveInfo) -> User:
        return cast(User, info.context.user)

    @staticmethod
    def resolve_user(root: None, info: ResolveInfo, id: ID = None) -> Optional[User]:
        try:
            # Ignore: Mypy complains that `get(pk=None)` is not valid. It might not be
            # the most sensible thing, but it actually doesn't fail at runtime.
            return get_user_model().objects.filter(is_superuser=False).get(pk=id)  # type: ignore[misc]
        except User.DoesNotExist:
            return None

    @staticmethod
    def resolve_created_courses(
        root: None,
        info: ResolveInfo,
        user: ID = None,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> graphene.ObjectType:
        if user is not None and user != info.context.user.pk:
            user_from_db = get_user_model().objects.get_or_none(pk=user)
        else:
            user_from_db = cast(User, info.context.user)

        if user_from_db is not None:
            qs: QuerySet[Course] = user_from_db.created_courses.all()
        else:
            # The user with the provided ID does not exist, we return an empty list.
            qs = Course.objects.none()

        return get_paginator(qs, page_size, page, PaginatedCourseObjectType)

    @staticmethod
    def resolve_created_resources(
        root: None,
        info: ResolveInfo,
        user: ID = None,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> graphene.ObjectType:
        if user is not None and user != info.context.user.pk:
            user_from_db = get_user_model().objects.get_or_none(pk=user)
        else:
            user_from_db = cast(User, info.context.user)

        if user_from_db is not None:
            qs: QuerySet[Resource] = user_from_db.created_resources.all()
        else:
            # The user with the provided ID does not exist, we return an empty list.
            qs = Resource.objects.none()

        return get_paginator(qs, page_size, page, PaginatedResourceObjectType)

    @staticmethod
    def resolve_starred_courses(
        root: None,
        info: ResolveInfo,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> QuerySet[Course]:
        qs = Course.objects.filter(stars__user__pk=info.context.user.pk)
        return get_paginator(qs, page_size, page, PaginatedCourseObjectType)

    @staticmethod
    def resolve_starred_resources(
        root: None,
        info: ResolveInfo,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> QuerySet[Resource]:
        qs = Resource.objects.filter(stars__user__pk=info.context.user.pk)
        return get_paginator(qs, page_size, page, PaginatedResourceObjectType)
