from typing import Optional

import graphene
from django.conf import settings
from django.db.models import QuerySet

from skole.models import Subject
from skole.schemas.base import SkoleDjangoObjectType, SkoleObjectType
from skole.schemas.mixins import PaginationMixin
from skole.types import ResolveInfo
from skole.utils.pagination import get_paginator


class SubjectObjectType(SkoleDjangoObjectType):
    slug = graphene.String()
    name = graphene.String()

    class Meta:
        model = Subject
        fields = ("id", "slug", "name")


class PaginatedSubjectObjectType(PaginationMixin, SkoleObjectType):
    objects = graphene.List(SubjectObjectType)

    class Meta:
        description = Subject.__doc__


class Query(SkoleObjectType):
    subjects = graphene.Field(
        PaginatedSubjectObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
    )

    autocomplete_subjects = graphene.List(
        SubjectObjectType,
        name=graphene.String(),
    )

    subject = graphene.Field(SubjectObjectType, slug=graphene.String())

    @staticmethod
    def resolve_subjects(
        root: None,
        info: ResolveInfo,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> PaginatedSubjectObjectType:
        """
        Filter results based on the school ID.

        Results are sorted alphabetically.
        """
        qs = Subject.objects.translated().order_by("translations__name")
        return get_paginator(qs, page_size, page, PaginatedSubjectObjectType)

    @staticmethod
    def resolve_autocomplete_subjects(
        root: None, info: ResolveInfo, name: str = ""
    ) -> QuerySet[Subject]:
        """Results are sorted alphabetically."""
        if name != "":
            qs = Subject.objects.translated(name__icontains=name)
        else:
            qs = Subject.objects.translated()

        qs = qs.order_by("translations__name")
        return qs[: settings.AUTOCOMPLETE_MAX_RESULTS]

    @staticmethod
    def resolve_subject(
        root: None, info: ResolveInfo, slug: str = ""
    ) -> Optional[Subject]:
        return Subject.objects.get_or_none(slug=slug)
