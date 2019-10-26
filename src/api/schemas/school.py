import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import to_global_id
from core.models import School


class SchoolType(DjangoObjectType):
    school_type = graphene.String()
    
    class Meta:
        model = School

    def resolve_school_type(self, info):
        return self.get_school_type_display()


class Query(graphene.ObjectType):
    school_list = graphene.List(SchoolType)
    school = graphene.Field(SchoolType, id=graphene.Int())

    def resolve_school_list(self, info):
        return School.objects.all()

    def resolve_school(self, info, id):
        return School.objects.get(pk=id)
