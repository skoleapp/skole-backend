from __future__ import annotations

from typing import Any, cast

import graphene
from graphene import NonNull

from skole.models import Thread, User
from skole.schemas.base import SkoleObjectType
from skole.types import JsonDict, ResolveInfo


class SitemapEntryObjectType(SkoleObjectType):
    slug = graphene.String()
    modified = graphene.Date()


class SitemapObjectType(SkoleObjectType):
    threads = NonNull(graphene.List(NonNull(SitemapEntryObjectType)))
    users = NonNull(graphene.List(NonNull(SitemapEntryObjectType)))


class Query(SkoleObjectType):
    sitemap = graphene.Field(SitemapObjectType)

    @staticmethod
    def resolve_sitemap(root: None, info: ResolveInfo) -> JsonDict:
        """Return the dynamic page slugs that frontend needs to build a
        `sitemap.xml`."""
        # pylint: disable=protected-access
        sitemap = {}

        for model in (Thread, User):
            # Without this `Any` typing here, Mypy would crash with the error:
            # `AttributeError: 'NoneType' object has no attribute 'name'`, on line 38.
            qs: Any = model.objects.order_by("pk")

            if model is User:
                qs = qs.filter(is_superuser=False)

            if hasattr(model, "modified"):
                values = (
                    SitemapEntryObjectType(slug, modified)
                    for (slug, modified) in qs.values_list("slug", "modified")
                )

            else:
                values = (
                    SitemapEntryObjectType(slug, None)
                    for slug in qs.values_list("slug", flat=True)
                )

            sitemap[cast(str, model._meta.verbose_name_plural)] = values

        return sitemap
