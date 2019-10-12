import graphene
import graphql_jwt
from django import forms
from graphene_django.forms.mutation import DjangoFormMutation
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType


class UserNodePublic(DjangoObjectType):
    class Meta:
        model = get_user_model()
        interfaces = (graphene.Node,)
        fields = ("id", "username", "title", "bio", "points", "created")


class UserNodePrivate(DjangoObjectType):
    class Meta:
        model = get_user_model()
        interfaces = (graphene.Node,)
        fields = ("id", "username", "title", "bio", "points", "created", "email", "language")


class RegisterForm(forms.ModelForm):
    password = forms.CharField(min_length=6)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password")


class RegisterMutation(DjangoFormMutation):
    user = graphene.Field(UserNodePrivate)

    class Meta:
        form_class = RegisterForm

    @classmethod
    def perform_mutate(cls, form, info):
        user = get_user_model().objects.create_user(
            email=form.cleaned_data["email"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        return RegisterMutation(user=user)


class Query(graphene.ObjectType):
    user = graphene.Node.Field(UserNodePublic)
    user_list = graphene.List(UserNodePublic)
    user_me = graphene.Field(UserNodePrivate)

    def resolve_user_list(self, info):
        return get_user_model().objects.all()

    def resolve_user_me(self, info):
        return get_user_model().objects.get(pk=info.context.user.id)


class Mutation(graphene.ObjectType):
    register = RegisterMutation.Field()
    login = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

# TODO: delete user
# TODO: update user
# TODO: change password
