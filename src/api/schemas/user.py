import graphene
from django import forms
from graphene_django.forms.mutation import DjangoFormMutation
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType


class UserTypePublic(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "title", "bio", "points", "created")


class UserTypePrivate(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "title", "bio", "points", "created", "email", "language")


class Query(graphene.ObjectType):
    all_users = graphene.List(UserTypePublic)
    user = graphene.Field(UserTypePublic, id=graphene.Int())
    user_me = graphene.Field(UserTypePrivate)

    def resolve_all_users(self, info, **kwargs):
        return get_user_model().objects.all()

    def resolve_user(self, info, id):
        return get_user_model().objects.get(pk=id)

    def resolve_user_me(self, info):
        return get_user_model().objects.get(pk=info.context.user.id)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(min_length=6)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password")


class RegisterMutation(DjangoFormMutation):
    user = graphene.Field(UserTypePrivate)

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


class Mutation(graphene.ObjectType):
    register = RegisterMutation.Field()
