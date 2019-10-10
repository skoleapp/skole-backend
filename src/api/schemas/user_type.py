import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType


class UserTypePublic(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "title", "bio", "points", "created", "email")

    def resolve_email(self):
        raise AssertionError()


class UserTypePrivate(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "title", "bio", "points", "created", "email", "language")


class Query(object):
    all_users = graphene.List(UserTypePublic)
    user = graphene.Field(UserTypePublic, user_id=graphene.Int())
    me = graphene.Field(UserTypePrivate)

    def resolve_all_users(self, info, **kwargs):
        return get_user_model().objects.all()

    def resolve_user(self, info, user_id):
        if info.context.user.id == user_id:
            res = UserTypePrivate()
            return self.resolve_me(info)
        return get_user_model().objects.get(pk=user_id)

    def resolve_me(self, info):
        return get_user_model().objects.get(pk=info.context.user.id)

