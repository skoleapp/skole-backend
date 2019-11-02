from typing import List, Any

from graphql import ResolveInfo

from core.models import User
from core.utils import JsonDict
from ..forms import RegisterForm, ChangePasswordForm, UpdateUserForm
import graphene
from graphql_jwt import JSONWebTokenMutation
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphql_extensions.auth.decorators import login_required
from ..utils import USER_DELETED_MESSAGE


class UserTypeRegister(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "created")


class UserTypePublic(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "title", "bio", "avatar", "avatar_thumbnail", "points", "created")


class UserTypePrivate(DjangoObjectType):
    language = graphene.String()

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "title", "bio", "avatar", "avatar_thumbnail", "points", "created", "email", "language")

    def resolve_language(self, info: ResolveInfo) -> str:
        return self.get_language_display()


class UserTypeChangePassword(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "modified")


class RegisterMutation(DjangoModelFormMutation):
    user = graphene.Field(UserTypeRegister)

    class Meta:
        form_class = RegisterForm

    @classmethod
    def perform_mutate(cls, form: RegisterForm, info: ResolveInfo) -> 'RegisterMutation':
        user = get_user_model().objects.create_user(
            email=form.cleaned_data["email"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )

        return cls(user=user)


class LoginMutation(JSONWebTokenMutation):
    user = graphene.Field(UserTypePrivate)

    @classmethod
    def resolve(cls, root: Any, info: ResolveInfo, **kwargs: Any) -> 'LoginMutation':
        return cls(user=info.context.user)


class ChangePasswordMutation(DjangoModelFormMutation):
    user = graphene.Field(UserTypeChangePassword)

    class Meta:
        form_class = ChangePasswordForm

    @classmethod
    def get_form_kwargs(cls, root: Any, info: ResolveInfo, **input: JsonDict) -> JsonDict:
        return {"data": input, "instance": info.context.user}

    @classmethod
    @login_required
    def perform_mutate(cls, form: ChangePasswordForm, info: ResolveInfo) -> 'ChangePasswordMutation':
        return cls(user=info.context.user)


class DeleteUserMutation(graphene.Mutation):
    message = graphene.String()

    @login_required
    def mutate(self, info: ResolveInfo) -> 'DeleteUserMutation':
        info.context.user.delete()
        return DeleteUserMutation(message=USER_DELETED_MESSAGE)


class UpdateUserMutation(DjangoModelFormMutation):
    user = graphene.Field(UserTypePrivate)

    class Meta:
        form_class = UpdateUserForm

    @classmethod
    def get_form_kwargs(cls, root: Any, info: ResolveInfo, **input: JsonDict) -> JsonDict:
        return {"data": input, "instance": info.context.user}

    @classmethod
    @login_required
    def perform_mutate(cls, form: UpdateUserForm, info: ResolveInfo) -> 'UpdateUserMutation':
        files = info.context.FILES
        user = info.context.user
        get_user_model().objects.update_user(user, **form.cleaned_data)
        return cls(user=user)


class Query(graphene.ObjectType):
    user_list = graphene.List(UserTypePublic)
    user = graphene.Field(UserTypePublic, id=graphene.Int())
    user_me = graphene.Field(UserTypePrivate)

    def resolve_user_list(self, info: ResolveInfo) -> List[User]:
        return get_user_model().objects.all()

    def resolve_user(self, info: ResolveInfo, id: int) -> User:
        return get_user_model().objects.get(pk=id)

    @login_required
    def resolve_user_me(self, info: ResolveInfo) -> User:
        return info.context.user


class Mutation(graphene.ObjectType):
    register = RegisterMutation.Field()
    login = LoginMutation.Field()
    # verify_token = graphql_jwt.Verify.Field()
    # refresh_token = graphql_jwt.Refresh.Field()
    update_user = UpdateUserMutation.Field()
    change_password = ChangePasswordMutation.Field()
    delete_user = DeleteUserMutation.Field()
