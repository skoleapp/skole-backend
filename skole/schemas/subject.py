from typing import Optional

import graphene
from django.conf import settings
from django.db.models import Count, QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import Subject
from skole.schemas.mixins import PaginationMixin
from skole.types import ID


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

    def resolve_autocomplete_subjects(
        self, info: ResolveInfo, name: str = ""
    ) -> QuerySet[Subject]:
        """
        Used for queries made by the client's auto complete fields.

        We want to avoid making massive queries by limiting the amount of results. If no
        school name is provided as a parameter, we return subjects with the most
        courses.
        """

        assert info.context is not None
        qs = Subject.objects.translated()

        if name != "":
            qs = qs.filter(translations__name__icontains=name)

        qs = qs.annotate(num_courses=Count("courses")).order_by(
            "-num_courses", "translations__name"
        )
        return qs[: settings.AUTOCOMPLETE_MAX_RESULTS]

    def resolve_subject(self, info: ResolveInfo, id: ID = None) -> Optional[Subject]:
        return Subject.objects.get_or_none(pk=id)
