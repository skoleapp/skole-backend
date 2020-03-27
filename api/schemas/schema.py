import graphene

import api.schemas.city
import api.schemas.comment
import api.schemas.contact
import api.schemas.country
import api.schemas.course
import api.schemas.resource
import api.schemas.resource_type
import api.schemas.school
import api.schemas.school_type
import api.schemas.star
import api.schemas.subject
import api.schemas.user
import api.schemas.vote


class Query(
    api.schemas.city.Query,
    api.schemas.comment.Query,
    api.schemas.country.Query,
    api.schemas.course.Query,
    api.schemas.resource.Query,
    api.schemas.resource_type.Query,
    api.schemas.school.Query,
    api.schemas.school_type.Query,
    api.schemas.subject.Query,
    api.schemas.user.Query,
):
    pass


class Mutation(
    api.schemas.comment.Mutation,
    api.schemas.contact.Mutation,
    api.schemas.course.Mutation,
    api.schemas.resource.Mutation,
    api.schemas.user.Mutation,
    api.schemas.vote.Mutation,
    api.schemas.star.Mutation,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
