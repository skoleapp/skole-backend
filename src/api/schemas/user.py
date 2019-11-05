from graphql_jwt.decorators import token_auth
from ..forms import RegisterForm, ChangePasswordForm, UpdateUserForm, LoginForm
import graphene
from graphql_jwt import JSONWebTokenMutation
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoFormMutation, DjangoModelFormMutation
from graphql_extensions.auth.decorators import login_required
from graphene_django.types import ErrorType
from ..utils import USER_DELETED_MESSAGE, USER_REGISTERED_MESSAGE, PASSWORD_SET_MESSAGE


class UserTypeRegister(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "message", "created")
    
    message = graphene.String()

    def resolve_message(self, info):
        return USER_REGISTERED_MESSAGE


class UserTypePublic(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "title", "bio", "avatar", "avatar_thumbnail", "points", "created")


class UserTypePrivate(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "title", "bio", "avatar", "avatar_thumbnail", "points", "created", "email", "language")


class UserTypeChangePassword(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "message", "modified")
    
    message = graphene.String()

    def resolve_message(self, info):
        return PASSWORD_SET_MESSAGE


class RegisterMutation(DjangoModelFormMutation):
    user = graphene.Field(UserTypeRegister)

    class Meta:
        form_class = RegisterForm

    @classmethod
    def perform_mutate(cls, form, info):
        user = get_user_model().objects.create_user(
            email=form.cleaned_data["email"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )

        return cls(user=user)


class LoginMutation(DjangoFormMutation):
    token = graphene.String()
    user = graphene.Field(UserTypePrivate)

    class Meta:
        form_class = LoginForm

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        form = cls.get_form(root, info, **input)

        if form.is_valid():
            password = form.cleaned_data["password"]
            user = form.cleaned_data["user"]
            return cls.perform_mutate(root=root, info=info, password=password, user=user, email=user.email)
        else:
            errors = ErrorType.from_errors(form.errors)
            return cls(errors=errors)

    @classmethod
    @token_auth
    def perform_mutate(cls, root, info, user, **kwargs):
        return cls(user=user)


class ChangePasswordMutation(DjangoModelFormMutation):
    user = graphene.Field(UserTypeChangePassword)

    class Meta:
        form_class = ChangePasswordForm

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        kwargs = {"data": input}
        kwargs["instance"] = info.context.user
        return kwargs

    @classmethod
    @login_required
    def perform_mutate(cls, form, info):
        return cls(user=info.context.user)


class DeleteUserMutation(graphene.Mutation):
    message = graphene.String()

    @login_required
    def mutate(self, info):
        info.context.user.delete()
        return DeleteUserMutation(message=USER_DELETED_MESSAGE)


class UpdateUserMutation(DjangoFormMutation):
    user = graphene.Field(UserTypePrivate)

    class Meta:
        form_class = UpdateUserForm

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        kwargs = {"data": input}
        kwargs["instance"] = info.context.user
        return kwargs

    @classmethod
    @login_required
    def perform_mutate(cls, form, info):
        files = info.context.FILES
        user = info.context.user
        get_user_model().objects.update_user(user, **form.cleaned_data)
        return cls(user=user)


class Query(graphene.ObjectType):
    user_list = graphene.List(UserTypePublic)
    user = graphene.Field(UserTypePublic, id=graphene.Int())
    user_me = graphene.Field(UserTypePrivate)

    def resolve_user_list(self, info):
        return get_user_model().objects.all()

    def resolve_user(self, info, id):
        return get_user_model().objects.get(pk=id)

    @login_required
    def resolve_user_me(self, info):
        return info.context.user


class Mutation(graphene.ObjectType):
    register = RegisterMutation.Field()
    login = LoginMutation.Field()
    update_user = UpdateUserMutation.Field()
    change_password = ChangePasswordMutation.Field()
    delete_user = DeleteUserMutation.Field()
