from typing import Optional

import graphene
from django.db.models import Count, QuerySet
from graphene_django import DjangoObjectType
from graphql import ResolveInfo

from skole.models import Subject
from skole.schemas.mixins import PaginationMixin
from skole.types import ID
from skole.utils.constants import MAX_QUERY_RESULTS
from skole.utils.shortcuts import get_obj_or_none


class SubjectObjectType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = Subject
        fields = ("id", "name")


class PaginatedSubjectObjectType(PaginationMixin, graphene.ObjectType):
    objects = graphene.List(SubjectObjectType)


class Query(graphene.ObjectType):
    # Used for non-paginated queries such as auto complete field results.
    subjects = graphene.List(SubjectObjectType, name=graphene.String())
    subject = graphene.Field(SubjectObjectType, id=graphene.ID())

    # We want to avoid making massive queries for instance in auto complete fields so we slice the results from this non-paginated query.
    # If no subject name is provided as a parameter, we return only the subjects that have the most courses so that at least some results are always returned.
    def resolve_subjects(
        self, info: ResolveInfo, name: str = ""
    ) -> "QuerySet[Subject]":
        assert info.context is not None
        qs = Subject.objects.translated(info.context.LANGUAGE_CODE).order_by(
            "translations__name"
        )

        if name != "":
            qs = qs.filter(name__icontains=name)
        else:
            qs = qs.annotate(num_courses=Count("courses")).order_by("-num_courses")

        return qs[:MAX_QUERY_RESULTS]

    def resolve_subject(self, info: ResolveInfo, id: ID = None) -> Optional[Subject]:
        return get_obj_or_none(Subject, id)
