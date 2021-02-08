from typing import Any, cast

import graphene
from graphene import NonNull

from skole.models import Course, Resource, School, User
from skole.schemas.base import SkoleObjectType
from skole.types import JsonDict, ResolveInfo


class SitemapEntryObjectType(SkoleObjectType):
    id = graphene.NonNull(graphene.ID)
    modified = graphene.Date()


class SitemapObjectType(SkoleObjectType):
    courses = NonNull(graphene.List(NonNull(SitemapEntryObjectType)))
    resources = NonNull(graphene.List(NonNull(SitemapEntryObjectType)))
    schools = NonNull(graphene.List(NonNull(SitemapEntryObjectType)))
    users = NonNull(graphene.List(NonNull(SitemapEntryObjectType)))


class Query(SkoleObjectType):
    sitemap = graphene.Field(SitemapObjectType)

    @staticmethod
    def resolve_sitemap(root: None, info: ResolveInfo) -> JsonDict:
        """Return the dynamic page IDs that frontend needs to build a `sitemap.xml`."""
        # pylint: disable=protected-access
        sitemap = {}

        for model in (Course, Resource, School, User):
            # Without this `Any` typing here, Mypy would crash with the error:
            # `AttributeError: 'NoneType' object has no attribute 'name'`, on line 38.
            qs: Any = model.objects.order_by("pk")
            if hasattr(model, "modified"):
                values = (
                    SitemapEntryObjectType(pk, modified)
                    for (pk, modified) in qs.values_list("pk", "modified")
                )
            else:
                values = (
                    SitemapEntryObjectType(pk, None)
                    for pk in qs.values_list("pk", flat=True)
                )
            sitemap[cast(str, model._meta.verbose_name_plural)] = values

        return sitemap
