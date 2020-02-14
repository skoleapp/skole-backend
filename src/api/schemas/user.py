from typing import Any, List, Optional, Union

import graphene
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphene_django.types import ErrorType
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required, token_auth
from mypy.types import JsonDict

from api.forms.user import (
    ChangePasswordForm,
    DeleteUserForm,
    LoginForm,
    RegisterForm,
    UpdateUserForm,
)
from api.utils.common import get_obj_or_none
from api.utils.points import get_points_for_user
from app.models import BetaCode, User


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
            "votes",
        )

    def resolve_email(self, info: ResolveInfo) -> str:
        """
        Return email only if authenticated and querying
        through userMe query or user query with own ID.
        """
        user = info.context.user

        if not user.is_anonymous and user.email == self.email:
            return self.email
        else:
            return ""

    def resolve_points(self, info: ResolveInfo) -> int:
        return get_points_for_user(self)

    def resolve_course_count(self, info: ResolveInfo) -> int:
        return self.created_courses.count()

    def resolve_resource_count(self, info: ResolveInfo) -> int:
        return self.created_resources.count()


class RegisterMutation(DjangoModelFormMutation):
    class Meta:
        form_class = RegisterForm
        exclude_fields = ("id",)

    @classmethod
    def perform_mutate(
        cls, form: RegisterForm, info: ResolveInfo
    ) -> "RegisterMutation":
        user = get_user_model().objects.create_user(
            email=form.cleaned_data["email"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )

        code = form.cleaned_data["code"]
        code.user = user
        code.save()

        return cls(user=user)


class LoginMutation(DjangoModelFormMutation):
    token = graphene.String()

    class Meta:
        form_class = LoginForm
        exclude_fields = ("id",)

    @classmethod
    def mutate_and_get_payload(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> "LoginMutation":
        form = cls.get_form(root, info, **input)

        if form.is_valid():
            password = form.cleaned_data["password"]
            user = form.cleaned_data["user"]
            return cls.perform_mutate(
                # @token_auth decorator changes the signature of perform_mutate to expect
                # exactly these params.
                root=root,
                info=info,
                password=password,
                user=user,
                email=user.email,
            )
        else:
            errors = ErrorType.from_errors(form.errors)
            return cls(errors=errors)

    @classmethod
    @token_auth
    def perform_mutate(
        cls, form: LoginForm, info: ResolveInfo, user: User, **kwargs: JsonDict
    ) -> "LoginMutation":
        return cls(user=user)


class ChangePasswordMutation(DjangoModelFormMutation):
    class Meta:
        form_class = ChangePasswordForm
        exclude_fields = ("id",)

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
        exclude_fields = ("id",)
        return_field_name = "message"

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
        return cls(message=_("User deleted successfully!"))


class UpdateUserMutation(DjangoModelFormMutation):
    class Meta:
        form_class = UpdateUserForm
        exclude_fields = ("id",)

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
        user = info.context.user

        # Don't allow changing avatar to anything but a File or ""
        if form.cleaned_data["avatar"] != "":
            if file := info.context.FILES.get("1"):
                form.cleaned_data["avatar"] = file
            else:
                form.cleaned_data["avatar"] = user.avatar

        get_user_model().objects.update_user(user, **form.cleaned_data)
        return cls(user=user)


class Query(graphene.ObjectType):
    users = graphene.List(
        UserObjectType, username=graphene.String(), ordering=graphene.String()
    )
    user = graphene.Field(UserObjectType, id=graphene.ID(required=True))
    user_me = graphene.Field(UserObjectType)

    def resolve_users(
        self,
        info: ResolveInfo,
        username: Optional[str] = None,
        ordering: Optional[str] = None,
    ) -> Union["QuerySet[User]", List[User]]:
        qs = get_user_model().objects.all()

        if username is not None:
            qs = qs.filter(username=username)

        if ordering in ["username", "-username"]:
            return qs.order_by(ordering)

        # FIXME: Add feature for resolving points in the model level.
        elif ordering in ["points", "-points"]:
            return sorted(qs, key=lambda u: get_points_for_user(u))

        return qs

    def resolve_user(self, info: ResolveInfo, id: int) -> Optional[User]:
        return get_obj_or_none(get_user_model(), id)

    @login_required
    def resolve_user_me(self, info: ResolveInfo) -> User:
        return info.context.user


class Mutation(graphene.ObjectType):
    login = LoginMutation.Field()
    register = RegisterMutation.Field()
    update_user = UpdateUserMutation.Field()
    change_password = ChangePasswordMutation.Field()
    delete_user = DeleteUserMutation.Field()
