import graphene

import skole.schemas.activity
import skole.schemas.city
import skole.schemas.comment
import skole.schemas.contact
import skole.schemas.country
import skole.schemas.course
import skole.schemas.resource
import skole.schemas.resource_type
import skole.schemas.school
import skole.schemas.school_type
import skole.schemas.star
import skole.schemas.subject
import skole.schemas.user
import skole.schemas.vote


class Query(
    skole.schemas.user.Query,
    skole.schemas.activity.Query,
    skole.schemas.city.Query,
    skole.schemas.country.Query,
    skole.schemas.course.Query,
    skole.schemas.resource.Query,
    skole.schemas.resource_type.Query,
    skole.schemas.school.Query,
    skole.schemas.school_type.Query,
    skole.schemas.subject.Query,
):
    pass


class Mutation(
    skole.schemas.activity.Mutation,
    skole.schemas.comment.Mutation,
    skole.schemas.contact.Mutation,
    skole.schemas.course.Mutation,
    skole.schemas.resource.Mutation,
    skole.schemas.user.Mutation,
    skole.schemas.vote.Mutation,
    skole.schemas.star.Mutation,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
