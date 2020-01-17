from typing import Any, List, Optional

from mypy.types import JsonDict

import graphene
from api.forms.user import (
    ChangePasswordForm,
    DeleteUserForm,
    SignInForm,
    SignUpForm,
    UpdateUserForm,
)
from api.utils.messages import USER_DELETED_MESSAGE
from api.utils.points import get_points_for_user
from app.models import User
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphene_django.types import ErrorType
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required, token_auth


class UserObjectType(DjangoObjectType):
    email = graphene.String()
    avatar = graphene.String()
    avatar_thumbnail = graphene.String()
    points = graphene.Int()
    course_count = graphene.Int()
    resource_count = graphene.Int()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "title",
            "bio",
            "avatar",
            "created",
            "created_courses",
            "created_resources",
        )

    def resolve_email(self, info: ResolveInfo) -> Optional[str]:
        """
        Return email only if authenticated and querying
        through userMe query or user query with own ID. 
        """
        user = info.context.user

        if not user.is_anonymous and user.email == self.email:
            return self.email
        else:
            return None

    def resolve_points(self, info: ResolveInfo) -> int:
        return get_points_for_user(self)

    def resolve_course_count(self, info: ResolveInfo) -> int:
        return self.created_courses.count()

    def resolve_resource_count(self, info: ResolveInfo) -> int:
        return self.created_resources.count()

    def resolve_avatar(self, info: ResolveInfo) -> str:
        if not self.avatar:
            return "static/default_avatar.jpg"
        else:
            return f"media/{self.avatar}"

    def resolve_avatar_thumbnail(self, info: ResolveInfo) -> str:
        if not self.avatar_thumbnail:
            return "static/default_avatar_thumbnail.jpg"
        else:
            return f"media/{self.avatar_thumbnail}"


class SignUpMutation(DjangoModelFormMutation):
    class Meta:
        form_class = SignUpForm

    @classmethod
    def perform_mutate(cls, form: SignUpForm, info: ResolveInfo) -> "SignUpForm":
        user = get_user_model().objects.create_user(
            email=form.cleaned_data["email"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )

        return cls(user=user)


class SignInMutation(DjangoModelFormMutation):
    token = graphene.String()

    class Meta:
        form_class = SignInForm

    @classmethod
    def mutate_and_get_payload(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> "SignInMutation":
        form = cls.get_form(root, info, **input)

        if form.is_valid():
            password = form.cleaned_data["password"]
            user = form.cleaned_data["user"]
            return cls.perform_mutate(
                root=root, info=info, password=password, user=user, email=user.email
            )
        else:
            errors = ErrorType.from_errors(form.errors)
            return cls(errors=errors)

    @classmethod
    @token_auth
    def perform_mutate(
        cls, form: SignInForm, info: ResolveInfo, user: User, **kwargs: JsonDict
    ) -> "SignInMutation":
        return cls(user=user)


class ChangePasswordMutation(DjangoModelFormMutation):
    class Meta:
        form_class = ChangePasswordForm

    @classmethod
    def get_form_kwargs(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> JsonDict:
        return {"data": input, "instance": info.context.user}

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: ChangePasswordForm, info: ResolveInfo
    ) -> "ChangePasswordMutation":
        return cls(user=info.context.user)


class DeleteUserMutation(DjangoModelFormMutation):
    message = graphene.String()

    class Meta:
        form_class = DeleteUserForm

    @classmethod
    def get_form_kwargs(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> JsonDict:
        return {"data": input, "instance": info.context.user}

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: DeleteUserForm, info: ResolveInfo
    ) -> "DeleteUserMutation":
        info.context.user.delete()
        return cls(message=USER_DELETED_MESSAGE)


class UpdateUserMutation(DjangoModelFormMutation):
    class Meta:
        form_class = UpdateUserForm

    @classmethod
    def get_form_kwargs(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> JsonDict:
        return {"data": input, "instance": info.context.user}

    @classmethod
    @login_required
    def perform_mutate(
        cls, form: UpdateUserForm, info: ResolveInfo
    ) -> "UpdateUserMutation":
        if file := info.context.FILES.get("1"):
            form.cleaned_data["avatar"] = file
        else:
            form.cleaned_data["avatar"] = None

        user = info.context.user
        get_user_model().objects.update_user(user, **form.cleaned_data)
        return cls(user=user)


class Query(graphene.ObjectType):
    users = graphene.List(UserObjectType)
    user = graphene.Field(UserObjectType, user_id=graphene.Int(required=True))
    user_me = graphene.Field(UserObjectType)

    def resolve_users(self, info: ResolveInfo) -> List[User]:
        # TODO: add some sorting options for the frontend to use,
        #  so that api caller can sort by points or by oldest user etc.
        return get_user_model().objects.filter(is_superuser=False)

    def resolve_user(self, info: ResolveInfo, user_id: int) -> Optional[User]:
        try:
            return get_user_model().objects.filter(is_superuser=False).get(pk=user_id)
        except get_user_model().DoesNotExist:
            # Return None instead of throwing a GraphQL Error.
            return None

    @login_required
    def resolve_user_me(self, info: ResolveInfo) -> User:
        return info.context.user


class Mutation(graphene.ObjectType):
    sign_up = SignUpMutation.Field()
    sign_in = SignInMutation.Field()
    update_user = UpdateUserMutation.Field()
    change_password = ChangePasswordMutation.Field()
    delete_user = DeleteUserMutation.Field()
