import graphene

import api.schemas.school
import api.schemas.user


class Query(api.schemas.user.Query, api.schemas.school.Query):
    pass


class Mutation(api.schemas.user.Mutation):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
