import api.schemas.city
import api.schemas.comment
import api.schemas.contact
import api.schemas.country
import api.schemas.course
import api.schemas.resource
import api.schemas.school
import api.schemas.subject
import api.schemas.user
import graphene


class Query(
    api.schemas.comment.Query,
    api.schemas.course.Query,
    api.schemas.resource.Query,
    api.schemas.school.Query,
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
