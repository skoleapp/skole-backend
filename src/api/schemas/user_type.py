import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class Query(object):
    all_users = graphene.List(UserType)

    def resolve_all_users(self, info, **kwargs):
        return get_user_model().objects.all()
