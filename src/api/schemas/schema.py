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
import api.schemas.subject
import api.schemas.user


class Query(
    api.schemas.comment.Query,
    api.schemas.course.Query,
    api.schemas.resource.Query,
    api.schemas.resource_type.Query,
    api.schemas.school.Query,
    api.schemas.school_type.Query,
    api.schemas.subject.Query,
    api.schemas.user.Query,
    api.schemas.country.Query,
    api.schemas.city.Query,
):
    pass


class Mutation(
    api.schemas.comment.Mutation,
    api.schemas.contact.Mutation,
    api.schemas.course.Mutation,
    api.schemas.resource.Mutation,
    api.schemas.user.Mutation,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
