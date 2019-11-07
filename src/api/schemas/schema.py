import graphene

import api.schemas.school
import api.schemas.subject
import api.schemas.user


class Query(
    api.schemas.subject.Query,
    api.schemas.school.Query,
    api.schemas.user.Query,
):
    pass


class Mutation(api.schemas.user.Mutation):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
