from typing import List, Union

import graphene
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import QuerySet

from core.models import Course, Resource, User

_PaginableModels = Union[User, Course, Resource]


def get_paginator(
    qs: "Union[List[_PaginableModels], QuerySet[_PaginableModels]]",
    page_size: int,
    page: int,
    paginated_type: graphene.ObjectType,
) -> graphene.ObjectType:

    p = Paginator(qs, page_size)

    try:
        page_obj = p.page(page)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)

    if isinstance(qs, QuerySet):
        count = qs.count()
    elif isinstance(qs, list):
        count = len(qs)

    return paginated_type(
        page=page_obj.number,
        pages=p.num_pages,
        has_next=page_obj.has_next(),
        has_prev=page_obj.has_previous(),
        objects=page_obj.object_list,
        count=count,
    )


class PaginationMixin:
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    count = graphene.Int()
