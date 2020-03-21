import graphene
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


# src: https://gist.github.com/mbrochh/f92594ab8188393bd83c892ef2af25e6
def get_paginator(qs, page_size, page, paginated_type, **kwargs):
    p = Paginator(qs, page_size)

    try:
        page_obj = p.page(page)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    return paginated_type(
        page=page_obj.number,
        pages=p.num_pages,
        has_next=page_obj.has_next(),
        has_prev=page_obj.has_previous(),
        objects=page_obj.object_list,
        **kwargs
    )


class PaginationMixin:
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
