from __future__ import annotations

from smtplib import SMTPException
from typing import Any

import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import BadSignature, SignatureExpired
from graphene_django.forms.mutation import DjangoFormMutation, DjangoModelFormMutation
from graphene_django.types import ErrorType
from graphql import ResolveInfo
from graphql_jwt import DeleteJSONWebTokenCookie
from graphql_jwt.decorators import token_auth

from skole.forms import (
    ChangePasswordForm,
    DeleteUserForm,
    EmailForm,
    LoginForm,
    RegisterForm,
    SetPasswordForm,
    TokenForm,
    UpdateUserForm,
)
from skole.models import User
from skole.schemas.mixins import SkoleCreateUpdateMutationMixin, SuccessMessageMixin
from skole.types import JsonDict
from skole.utils.constants import Messages, MutationErrors, TokenAction
from skole.utils.exceptions import TokenScopeError, UserAlreadyVerified, UserNotVerified
from skole.utils.token import get_token_payload, revoke_user_refresh_tokens

from .object_types import UserObjectType


class RegisterMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """
    Register new user.

    Check if there is an existing user with that email or username. Check that account
    is not deactivated. By default set the user a unverified. After successful
    registration send account verification email.
    """

    success_message = Messages.USER_REGISTERED

    class Meta:
        form_class = RegisterForm
        exclude_fields = ("id",)
        return_field_name = "message"

    @classmethod
    def perform_mutate(cls, form: RegisterForm, info: ResolveInfo) -> RegisterMutation:
        obj = super().perform_mutate(form, info)

        try:
            form.instance.send_verification_email(info)
        except SMTPException:
            return cls(errors=MutationErrors.REGISTER_EMAIL_ERROR)

        return obj


class VerifyAccountMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoFormMutation
):
    """Receive the token that was sent by email, if the token is valid, verify the
    user's account."""

    class Meta:
        form_class = TokenForm

    @classmethod
    def perform_mutate(
        cls, form: TokenForm, info: ResolveInfo,
    ) -> VerifyAccountMutation:
        token = form.cleaned_data.get("token")

        try:
            get_user_model().objects.verify_user(token)
            return cls(message=Messages.ACCOUNT_VERIFIED)

        except UserAlreadyVerified:
            return cls(errors=MutationErrors.ALREADY_VERIFIED)

        except SignatureExpired:
            return cls(errors=MutationErrors.TOKEN_EXPIRED_VERIFY)

        except (BadSignature, TokenScopeError):
            return cls(errors=MutationErrors.INVALID_TOKEN_VERIFY)


class ResendVerificationEmailMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoFormMutation
):
    """
    Sends verification email again.

    Return error if a user with the provided email is not found.
    """

    class Meta:
        form_class = EmailForm

    @classmethod
    def perform_mutate(
        cls, form: EmailForm, info: ResolveInfo,
    ) -> ResendVerificationEmailMutation:
        email = form.cleaned_data.get("email")

        try:
            user = get_user_model().objects.get(email=email)
            user.resend_verification_email(info)
            return cls(message=Messages.VERIFICATION_EMAIL_SENT)

        except ObjectDoesNotExist:
            return cls(errors=MutationErrors.USER_NOT_FOUND_WITH_EMAIL)

        except SMTPException:
            return cls(errors=MutationErrors.EMAIL_ERROR)

        except UserAlreadyVerified:
            return cls(errors=MutationErrors.ALREADY_VERIFIED)


class SendPasswordResetEmailMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoFormMutation
):
    """
    Send password reset email.

    For non verified users, send an verification email instead. Return error if a user
    with the provided email is not found.
    """

    class Meta:
        form_class = EmailForm

    @classmethod
    def perform_mutate(
        cls, form: EmailForm, info: ResolveInfo,
    ) -> SendPasswordResetEmailMutation:
        email = form.cleaned_data.get("email")

        try:
            user = get_user_model().objects.get(email=email)
            user.send_password_reset_email(info, [email])
            return cls(message=Messages.PASSWORD_RESET_EMAIL_SENT)

        except ObjectDoesNotExist:
            return cls(errors=MutationErrors.USER_NOT_FOUND_WITH_EMAIL)

        except SMTPException:
            return cls(errors=MutationErrors.EMAIL_ERROR)

        except UserNotVerified:
            user = get_user_model().objects.get(email=email)

            try:
                user.resend_verification_email(info)
                return cls(errors=MutationErrors.NOT_VERIFIED_RESET_PASSWORD)

            except SMTPException:
                return cls(errors=MutationErrors.EMAIL_ERROR)


class ResetPasswordMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoFormMutation
):
    """
    Change user's password without old password.

    Receive the token that was sent by email. Revoke refresh token and thus require the
    user to log in with his new password.
    """

    class Meta:
        form_class = SetPasswordForm

    @classmethod
    def perform_mutate(
        cls, form: EmailForm, info: ResolveInfo,
    ) -> ResetPasswordMutation:
        token = form.cleaned_data.get("token")
        new_password = form.cleaned_data.get("new_password")

        try:
            payload = get_token_payload(
                token,
                TokenAction.PASSWORD_RESET,
                settings.EXPIRATION_PASSWORD_RESET_TOKEN,
            )

            user = get_user_model().objects.get(**payload)
            revoke_user_refresh_tokens(user)
            user = get_user_model().objects.set_password(
                user=user, password=new_password
            )

            return cls(message=Messages.PASSWORD_UPDATED)

        except ObjectDoesNotExist:
            return cls(errors=MutationErrors.ACCOUNT_REMOVED)

        except SignatureExpired:
            return cls(errors=MutationErrors.TOKEN_EXPIRED_RESET_PASSWORD)

        except (BadSignature, TokenScopeError):
            return cls(errors=MutationErrors.INVALID_TOKEN_RESET_PASSWORD)


class LoginMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """
    Obtain JSON web token and user information.

    Not verified users can still login.
    """

    user = graphene.Field(UserObjectType)

    class Meta:
        form_class = LoginForm
        exclude_fields = ("id",)

    @classmethod
    def mutate_and_get_payload(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> LoginMutation:
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
    ) -> LoginMutation:
        return cls(user=user, message=Messages.LOGGED_IN)


class LogoutMutation(DeleteJSONWebTokenCookie):
    """
    Delete JSON web token cookie and logout.

    This sets the `Set-Cookie` header so that the JWT token cookie gets automatically
    deleted in frontend.
    """


class ChangePasswordMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """
    Change account password when user knows the old password.

    User must be verified.
    """

    verification_required = True

    class Meta:
        form_class = ChangePasswordForm
        exclude_fields = ("id",)
        return_field_name = "message"

    @classmethod
    def get_form_kwargs(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> JsonDict:
        kwargs = super().get_form_kwargs(root, info, **input)
        assert info.context is not None
        kwargs["instance"] = info.context.user
        return kwargs

    @classmethod
    def perform_mutate(
        cls, form: ChangePasswordForm, info: ResolveInfo
    ) -> ChangePasswordMutation:
        assert info.context is not None
        new_password = form.cleaned_data["new_password"]

        get_user_model().objects.set_password(
            user=info.context.user, password=new_password
        )

        return cls(message=Messages.PASSWORD_UPDATED)


class DeleteUserMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """
    Delete account permanently.

    The user must confirm his password.
    """

    login_required = True

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
    def perform_mutate(
        cls, form: DeleteUserForm, info: ResolveInfo
    ) -> DeleteUserMutation:
        assert info.context is not None
        user = info.context.user
        user.soft_delete()
        return cls(message=Messages.USER_DELETED)


class UpdateUserMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """Update some user model fields."""

    login_required = True
    success_message = Messages.USER_UPDATED

    user = graphene.Field(UserObjectType)

    class Meta:
        form_class = UpdateUserForm
        exclude_fields = ("id",)

    @classmethod
    def get_form_kwargs(
        cls, root: Any, info: ResolveInfo, **input: JsonDict
    ) -> JsonDict:
        assert info.context is not None
        form_kwargs = super().get_form_kwargs(root, info, **input)
        form_kwargs["instance"] = info.context.user
        return form_kwargs


class Mutation(graphene.ObjectType):
    register = RegisterMutation.Field()
    verify_account = VerifyAccountMutation.Field()
    resend_verification_email = ResendVerificationEmailMutation.Field()
    send_password_reset_email = SendPasswordResetEmailMutation.Field()
    reset_password = ResetPasswordMutation.Field()
    login = LoginMutation.Field()
    logout = LogoutMutation.Field()
    update_user = UpdateUserMutation.Field()
    change_password = ChangePasswordMutation.Field()
    delete_user = DeleteUserMutation.Field()
