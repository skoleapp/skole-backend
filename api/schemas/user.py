from smtplib import SMTPException
from typing import Any, Literal, Optional

import graphene
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import BadSignature, SignatureExpired
from django.db.models import QuerySet
from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoFormMutation, DjangoModelFormMutation
from graphene_django.types import ErrorType
from graphql import GraphQLError, ResolveInfo
from graphql_auth.constants import TokenAction
from graphql_auth.exceptions import (
    TokenScopeError,
    UserAlreadyVerified,
    UserNotVerified,
)
from graphql_auth.models import UserStatus
from graphql_auth.settings import graphql_auth_settings
from graphql_auth.shortcuts import get_user_by_email
from graphql_auth.utils import get_token_paylod, revoke_user_refresh_token
from graphql_jwt.decorators import login_required, token_auth
from mypy.types import JsonDict

from api.forms.user import (
    ChangePasswordForm,
    DeleteUserForm,
    EmailForm,
    LoginForm,
    RegisterForm,
    SetPasswordForm,
    TokenForm,
    UpdateUserForm,
)
from api.schemas.course import CourseObjectType
from api.schemas.resource import ResourceObjectType
from api.utils.decorators import verification_required_mutation
from api.utils.file import FileMixin
from api.utils.messages import (
    ACCOUNT_ALREADY_VERIFIED_MESSAGE,
    EMAIL_ERROR_MESSAGE,
    USER_NOT_FOUND_WITH_PROVIDED_EMAIL_MESSAGE,
)
from api.utils.pagination import PaginationMixin, get_paginator
from core.models import BetaCode, Course, Resource, User


class UserObjectType(DjangoObjectType):
    email = graphene.String()
    score = graphene.Int()
    avatar = graphene.String()
    avatar_thumbnail = graphene.String()
    verified = graphene.Boolean()
    course_count = graphene.Int()
    resource_count = graphene.Int()
    starred_courses = graphene.List(CourseObjectType)
    starred_resources = graphene.List(ResourceObjectType)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "score",
            "title",
            "bio",
            "avatar",
            "avatar_thumbnail",
            "created",
            "verified",
            "course_count",
            "resource_count",
            "votes",
            "starred_courses",
            "starred_resources",
            "created_courses",
            "created_resources",
        )

    def resolve_email(self, info: ResolveInfo) -> str:
        """
        Return email only if authenticated and querying
        through userMe query or user query with own ID.
        """
        assert info.context is not None
        user = info.context.user

        if not user.is_anonymous and user.email == self.email:
            return self.email
        else:
            return ""

    def resolve_course_count(self, info: ResolveInfo) -> int:
        return self.created_courses.count()

    def resolve_resource_count(self, info: ResolveInfo) -> int:
        return self.created_resources.count()

    def resolve_avatar(self, info: ResolveInfo) -> str:
        return self.avatar.url if self.avatar else ""

    def resolve_avatar_thumbnail(self, info: ResolveInfo) -> str:
        return self.avatar_thumbnail.url if self.avatar_thumbnail else ""

    def resolve_verified(self, info: ResolveInfo) -> Optional[bool]:
        # We resolve this here rather than on model level
        # as we don't want to know the verification status
        # for anyone else as the user making the request.
        if self.id == info.context.user.pk:
            return info.context.user.status.verified
        else:
            return None

    def resolve_starred_courses(self, info: ResolveInfo) -> "QuerySet[Course]":
        return Course.objects.filter(stars__user__pk=self.pk)

    def resolve_starred_resources(self, info: ResolveInfo) -> "QuerySet[Resource]":
        return Resource.objects.filter(stars__user__pk=self.pk)


class PaginatedUserObjectType(PaginationMixin, graphene.ObjectType):
    objects = graphene.List(UserObjectType)


class RegisterMutation(DjangoModelFormMutation):
    """
    Register new user. Check if there is an existing user
    with that email or username. Check that account is not
    deactivated. When creating the user, also create `UserStatus`
    related to that user, making it possible to track
    if the user is archived, verified and has a secondary email.
    After successful registration send account verification email.
    """

    message = graphene.String()

    class Meta:
        form_class = RegisterForm
        exclude_fields = ("id",)
        return_field_name = "message"

    @classmethod
    def perform_mutate(
        cls, form: RegisterForm, info: ResolveInfo
    ) -> "RegisterMutation":
        user = get_user_model().objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )

        code = form.cleaned_data["code"]
        BetaCode.objects.decrement_usages(code)

        try:
            # Ignore: Mypy doesn't recognize relation between `User` and `UserStatus` models.
            user.status.send_activation_email(info)  # type: ignore [attr-defined]
        except SMTPException:
            return cls(
                errors=[{"field": "__all__", "messages": [EMAIL_ERROR_MESSAGE],}]
            )

        return cls(message=_("Registered new user successfully!"))


class VerifyAccountMutation(DjangoFormMutation):
    """
    Verify user account. Receive the token that was
    sent by email. If the token is valid, verify the
    user by making the `user.status.verified` field `True`.
    """

    message = graphene.String()

    class Meta:
        form_class = TokenForm

    @classmethod
    def perform_mutate(
        cls, form: TokenForm, info: ResolveInfo, **kwargs: JsonDict
    ) -> "VerifyAccountMutation":
        token = form.cleaned_data.get("token")

        try:
            UserStatus.verify(token)
            # TODO: Translate this.
            return cls(message=_("Account verified successfully!"))

        except UserAlreadyVerified:
            return cls(
                errors=[
                    {
                        "field": "__all__",
                        "messages": [ACCOUNT_ALREADY_VERIFIED_MESSAGE],
                    }
                ]
            )

        except SignatureExpired:
            return cls(
                errors=[
                    {
                        "field": "__all__",
                        "messages": [
                            # TODO: Translate this.
                            _("Token expired. Please request new activation link.")
                        ],
                    }
                ]
            )

        except (BadSignature, TokenScopeError):
            return cls(
                errors=[
                    {
                        "field": "__all__",
                        "messages": [
                            # TODO: Translate this.
                            _("Invalid token. Please request new activation link.")
                        ],
                    }
                ]
            )


class ResendVerificationEmailMutation(DjangoFormMutation):
    """
    Sends activation email again. Return error if
    a user with the provided email is not found.
    """

    message = graphene.String()

    class Meta:
        form_class = EmailForm

    @classmethod
    def perform_mutate(
        cls, form: EmailForm, info: ResolveInfo, **kwargs: JsonDict
    ) -> "ResendVerificationEmailMutation":
        email = form.cleaned_data.get("email")

        try:
            user = get_user_by_email(email)
            user.status.resend_activation_email(info)
            # TODO: Translate this.
            return cls(message=_("Verification email sent successfully!"))

        except ObjectDoesNotExist:
            return cls(
                errors=[
                    {
                        "field": "__all__",
                        "messages": [USER_NOT_FOUND_WITH_PROVIDED_EMAIL_MESSAGE],
                    }
                ]
            )

        except SMTPException:
            return cls(
                errors=[{"field": "__all__", "messages": [EMAIL_ERROR_MESSAGE],}]
            )

        except UserAlreadyVerified:
            return cls(
                errors=[
                    {
                        "field": "__all__",
                        "messages": [ACCOUNT_ALREADY_VERIFIED_MESSAGE],
                    }
                ]
            )


class SendPasswordResetEmailMutation(DjangoFormMutation):
    """
    Send password reset email. For non verified users,
    send an activation email instead. Return error
    if a user with the provided email is not found.
    """

    message = graphene.String()

    class Meta:
        form_class = EmailForm

    @classmethod
    def perform_mutate(
        cls, form: EmailForm, info: ResolveInfo, **kwargs: JsonDict
    ) -> "SendPasswordResetEmailMutation":
        email = form.cleaned_data.get("email")

        try:
            user = get_user_by_email(email)
            user.status.send_password_reset_email(info, [email])
            # TODO: Translate this.
            return cls(message=_("Password reset link sent successfully!"))

        except ObjectDoesNotExist:
            return cls(
                errors=[
                    {
                        "field": "__all__",
                        "messages": [USER_NOT_FOUND_WITH_PROVIDED_EMAIL_MESSAGE],
                    }
                ]
            )

        except SMTPException:
            return cls(
                errors=[{"field": "__all__", "messages": [EMAIL_ERROR_MESSAGE],}]
            )

        except UserNotVerified:
            user = get_user_by_email(email)

            try:
                user.status.resend_activation_email(info)

                return cls(
                    errors=[
                        # TODO: Translate this.
                        {
                            "field": "__all__",
                            "messages": [
                                _(
                                    "You must verify your account before resetting your password. A new verification email was sent. Please check your inbox and verify your account."
                                )
                            ],
                        }
                    ]
                )

            except SMTPException:
                return cls(
                    errors=[{"field": "__all__", "messages": [EMAIL_ERROR_MESSAGE],}]
                )


class ResetPasswordMutation(DjangoFormMutation):
    """
    Change user's password without old password.
    Receive the token that was sent by email.
    Revoke refresh token and thus require the
    user to log in with his new password.
    """

    message = graphene.String()

    class Meta:
        form_class = SetPasswordForm

    @classmethod
    def perform_mutate(
        cls, form: EmailForm, info: ResolveInfo, **kwargs: JsonDict
    ) -> "ResetPasswordMutation":
        token = form.cleaned_data.get("token")
        new_password = form.cleaned_data.get("new_password")

        try:
            payload = get_token_paylod(
                token,
                TokenAction.PASSWORD_RESET,
                graphql_auth_settings.EXPIRATION_PASSWORD_RESET_TOKEN,
            )

            user = get_user_model().objects.get(**payload)
            revoke_user_refresh_token(user)
            user = get_user_model().objects.set_password(
                user=user, password=new_password
            )
            return cls(
                message=_("Password updated successfully!")
            )  # TODO: Translate this.

        except ObjectDoesNotExist:
            return cls(
                errors=[
                    {
                        "field": "__all__",
                        "messages": _("This account has been removed."),
                    }
                ]
            )

        except SignatureExpired:
            return cls(
                errors=[
                    {
                        "field": "__all__",
                        "messages": [
                            # TODO: Translate this.
                            _("Token expired. Please request new password reset link.")
                        ],
                    }
                ]
            )

        except (BadSignature, TokenScopeError):
            return cls(
                errors=[
                    {
                        "field": "__all__",
                        "messages": [
                            # TODO: Translate this.
                            _("Invalid token. Please request new password reset link.")
                        ],
                    }
                ]
            )


class LoginMutation(DjangoModelFormMutation):
    """
    Obtain JSON web token and user information.
    Not verified users can still login.
    """

    token = graphene.String()
    user = graphene.Field(UserObjectType)
    message = graphene.String()

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
                username=user.username,
            )
        else:
            errors = ErrorType.from_errors(form.errors)
            return cls(errors=errors)

    @classmethod
    @token_auth
    def perform_mutate(
        cls, form: LoginForm, info: ResolveInfo, user: User, **kwargs: JsonDict
    ) -> "LoginMutation":
        # TODO: Translate this.
        return cls(user=user, message=_("Logged in successfully!"))


class ChangePasswordMutation(DjangoModelFormMutation):
    """Change account password when user knows the old password. User must be verified."""

    message = graphene.String()

    class Meta:
        form_class = ChangePasswordForm
        exclude_fields = ("id",)
        return_field_name = "message"

    @classmethod
    def get_form_kwargs(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> JsonDict:
        assert info.context is not None
        return {"data": input, "instance": info.context.user}

    @classmethod
    @verification_required_mutation
    def perform_mutate(
        cls, form: ChangePasswordForm, info: ResolveInfo
    ) -> "ChangePasswordMutation":
        assert info.context is not None
        new_password = form.cleaned_data["new_password"]
        get_user_model().objects.set_password(
            user=info.context.user, password=new_password
        )
        # TODO: Translate this.
        return cls(message=_("Password changed successfully!"))


class DeleteUserMutation(DjangoModelFormMutation):
    """Delete account permanently. User must be verified and confirm his password."""

    message = graphene.String()

    class Meta:
        form_class = DeleteUserForm
        exclude_fields = ("id",)
        return_field_name = "message"

    @classmethod
    def get_form_kwargs(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> JsonDict:
        assert info.context is not None
        return {"data": input, "instance": info.context.user}

    @classmethod
    @verification_required_mutation
    def perform_mutate(
        cls, form: DeleteUserForm, info: ResolveInfo
    ) -> "DeleteUserMutation":
        assert info.context is not None
        user = info.context.user
        user.delete()
        return cls(message=_("User deleted successfully."))


class UpdateUserMutation(FileMixin, DjangoModelFormMutation):
    """Update user model fields. User must be verified."""

    user = graphene.Field(UserObjectType)

    class Meta:
        form_class = UpdateUserForm
        exclude_fields = ("id",)

    @classmethod
    @verification_required_mutation
    def perform_mutate(
        cls, form: UpdateUserForm, info: ResolveInfo
    ) -> "UpdateUserMutation":
        assert info.context is not None
        user = info.context.user
        get_user_model().objects.update_user(user, **form.cleaned_data)
        return cls(user=user)


class Query(graphene.ObjectType):
    users = graphene.Field(
        PaginatedUserObjectType,
        page=graphene.Int(),
        page_size=graphene.Int(),
        username=graphene.String(),
        ordering=graphene.String(),
    )

    user = graphene.Field(UserObjectType, id=graphene.ID())
    user_me = graphene.Field(UserObjectType)

    @login_required
    def resolve_users(
        self,
        info: ResolveInfo,
        page: int = 1,
        page_size: int = 10,
        username: Optional[str] = None,
        ordering: Literal["username", "-username", "score", "-score"] = "username",
    ) -> graphene.ObjectType:
        qs = get_user_model().objects.filter(is_superuser=False)

        if username is not None:
            qs = qs.filter(username__icontains=username)

        if ordering not in {
            "username",
            "-username",
            "score",
            "-score",
        }:
            raise GraphQLError("Invalid ordering value.")

        if ordering not in {"username", "-username"}:
            # When ordering by score we also first order by the username.
            qs = qs.order_by("username")
        qs = qs.order_by(ordering)

        return get_paginator(qs, page_size, page, PaginatedUserObjectType)

    @login_required
    def resolve_user(
        self, info: ResolveInfo, id: Optional[int] = None
    ) -> Optional[User]:
        try:
            # Ignore: get() isn't typed to receive None, even if that doesn't give error.
            return get_user_model().objects.filter(is_superuser=False).get(pk=id)  # type: ignore[misc]
        except User.DoesNotExist:
            return None

    @login_required
    def resolve_user_me(self, info: ResolveInfo) -> User:
        assert info.context is not None
        return info.context.user


class Mutation(graphene.ObjectType):
    register = RegisterMutation.Field()
    verify_account = VerifyAccountMutation.Field()
    resend_verification_email = ResendVerificationEmailMutation.Field()
    send_password_reset_email = SendPasswordResetEmailMutation.Field()
    reset_password = ResetPasswordMutation.Field()
    login = LoginMutation.Field()
    update_user = UpdateUserMutation.Field()
    change_password = ChangePasswordMutation.Field()
    delete_user = DeleteUserMutation.Field()
