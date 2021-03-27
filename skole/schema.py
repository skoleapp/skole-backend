import graphene

import skole.schemas.activity
import skole.schemas.badge
import skole.schemas.comment
import skole.schemas.contact
import skole.schemas.gdpr
import skole.schemas.sitemap
import skole.schemas.star
import skole.schemas.thread
import skole.schemas.user
import skole.schemas.vote


class Query(
    skole.schemas.activity.Query,
    skole.schemas.thread.Query,
    skole.schemas.sitemap.Query,
    skole.schemas.user.Query,
    skole.schemas.comment.Query,
    skole.schemas.badge.Query,
):
    pass


class Mutation(
    skole.schemas.activity.Mutation,
    skole.schemas.comment.Mutation,
    skole.schemas.contact.Mutation,
    skole.schemas.thread.Mutation,
    skole.schemas.gdpr.Mutation,
    skole.schemas.user.Mutation,
    skole.schemas.vote.Mutation,
    skole.schemas.star.Mutation,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
