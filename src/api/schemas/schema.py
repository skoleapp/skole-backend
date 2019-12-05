import graphene

import api.schemas.course
import api.schemas.school
import api.schemas.subject
import api.schemas.user
import api.schemas.resource
import api.schemas.resource_type


class Query(
    api.schemas.course.Query,
    api.schemas.school.Query,
    api.schemas.subject.Query,
    api.schemas.user.Query,
    api.schemas.resource.Query,
    api.schemas.resource_type.Query
):
    pass


class Mutation(
    api.schemas.user.Mutation,
    api.schemas.course.Mutation,
):
    pass


# noinspection PyTypeChecker
schema = graphene.Schema(query=Query, mutation=Mutation)
