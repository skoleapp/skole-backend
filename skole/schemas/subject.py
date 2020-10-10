from typing import Optional

import graphene
from django.conf import settings
from django.db.models import Count, QuerySet
from graphene_django import DjangoObjectType

from skole.models import Subject
from skole.schemas.mixins import PaginationMixin
from skole.types import ID, ResolveInfo


class SubjectObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = Subject
        fields = ("id", "name")


class PaginatedSubjectObjectType(PaginationMixin, graphene.ObjectType):
    objects = graphene.List(SubjectObjectType)


class Query(graphene.ObjectType):
    autocomplete_subjects = graphene.List(SubjectObjectType, name=graphene.String())
    subject = graphene.Field(SubjectObjectType, id=graphene.ID())

    @staticmethod
    def resolve_autocomplete_subjects(
        root: None, info: ResolveInfo, name: str = ""
    ) -> QuerySet[Subject]:
        """
        Used for queries made by the client's auto complete fields.

        We want to avoid making massive queries by limiting the amount of results. If no
        school name is provided as a parameter, we return subjects with the most
        courses.
        """
        qs = Subject.objects.translated()

        if name != "":
            qs = qs.filter(translations__name__icontains=name)

        qs = qs.annotate(num_courses=Count("courses")).order_by(
            "-num_courses", "translations__name"
        )
        return qs[: settings.AUTOCOMPLETE_MAX_RESULTS]

    @staticmethod
    def resolve_subject(
        root: None, info: ResolveInfo, id: ID = None
    ) -> Optional[Subject]:
        return Subject.objects.get_or_none(pk=id)
