import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "title", "bio", "points", "created", "email", "language")


class Query(object):
    all_users = graphene.List(UserType)
    user = graphene.Field(UserType, user_id=graphene.Int())
    me = graphene.Field(UserType)

    def resolve_all_users(self, info, **kwargs):
        return get_user_model().objects.all()

    def resolve_user(self, info, user_id):
        user = get_user_model().objects.get(pk=user_id)
        if info.context.user.id != user_id:
            pass
        return user

    def resolve_me(self, info):
        return get_user_model().objects.get(pk=info.context.user.id)

