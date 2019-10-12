import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.models import School


class SchoolNode(DjangoObjectType):
    school_type = graphene.String()

    class Meta:
        model = School
        interfaces = (graphene.Node,)
        filter_fields = {
            "school_type": ("icontains",),
            "name": ("icontains",),
            "city": ("icontains",),
            "country": ("icontains",),
        }

    def resolve_school_type(self, info):
        return self.get_school_type_display()


class Query(graphene.ObjectType):
    school = graphene.Node.Field(SchoolNode)
    school_list = DjangoFilterConnectionField(SchoolNode)
