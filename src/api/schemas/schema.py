import graphene

import api.schemas.user_type


class Query(api.schemas.user_type.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
