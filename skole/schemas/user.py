from smtplib import SMTPException
from typing import Any, Optional

import graphene
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import BadSignature, SignatureExpired
from django.db.models import QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoFormMutation, DjangoModelFormMutation
from graphene_django.types import ErrorType
from graphql import ResolveInfo
from graphql_jwt.decorators import login_required, token_auth
from mypy.types import JsonDict

from skole.forms.user import (
    ChangePasswordForm,
    DeleteUserForm,
    EmailForm,
    LoginForm,
    RegisterForm,
    SetPasswordForm,
    TokenForm,
    UpdateUserForm,
)
from skole.models import Badge, BetaCode, Course, Resource, School, Subject, User
from skole.schemas.badge import BadgeObjectType
from skole.schemas.course import CourseObjectType
from skole.schemas.resource import ResourceObjectType
from skole.schemas.school import SchoolObjectType
from skole.schemas.subject import SubjectObjectType
from skole.utils.constants import Messages, MutationErrors, TokenAction
from skole.utils.exceptions import TokenScopeError, UserAlreadyVerified, UserNotVerified
from skole.utils.mixins import FileMutationMixin, VerificationRequiredMutationMixin
from skole.utils.token import get_token_payload, revoke_user_refresh_tokens


class UserObjectType(DjangoObjectType):
    email = graphene.String()
    score = graphene.Int()
    avatar = graphene.String()
    avatar_thumbnail = graphene.String()
    verified = graphene.Boolean()
    course_count = graphene.Int()
    resource_count = graphene.Int()
    school = graphene.Field(SchoolObjectType)
    subject = graphene.Field(SubjectObjectType)
    rank = graphene.String()
    badges = graphene.List(BadgeObjectType)
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
        assert info.context is not None

        # We resolve this here rather than on model level
        # as we don't want to know the verification status
        # for anyone else as the user making the request.
        if self.pk == info.context.user.pk:
            return info.context.user.verified
        else:
            return None

    def resolve_school(self, info: ResolveInfo) -> "School":
        assert info.context is not None
        return self.school if self.pk == info.context.user.pk else None

    def resolve_subject(self, info: ResolveInfo) -> "Subject":
        assert info.context is not None
        return self.subject if self.pk == info.context.user.pk else None

    def resolve_starred_courses(self, info: ResolveInfo) -> "QuerySet[Course]":
        return Course.objects.filter(stars__user__pk=self.pk)

    def resolve_starred_resources(self, info: ResolveInfo) -> "QuerySet[Resource]":
        return Resource.objects.filter(stars__user__pk=self.pk)

    def resolve_badges(self, info: ResolveInfo) -> "QuerySet[Badge]":
        return self.badges.all()


class RegisterMutation(DjangoModelFormMutation):
    """
    Register new user. Check if there is an existing user
    with that email or username. Check that account is not
    deactivated. By default set the user a unverified.
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
            school=form.cleaned_data["school"],
            subject=form.cleaned_data["subject"],
        )

        code = form.cleaned_data["code"]
        BetaCode.objects.decrement_usages(code)

        try:
            user.send_verification_email(info)
        except SMTPException:
            return cls(errors=MutationErrors.REGISTER_EMAIL_ERROR)

        return cls(message=Messages.USER_REGISTERED)


class VerifyAccountMutation(DjangoFormMutation):
    """
    Receive the token that was sent by email.
    If the token is valid, verify the user's account.
    """

    message = graphene.String()

    class Meta:
        form_class = TokenForm

    @classmethod
    def perform_mutate(
        cls, form: TokenForm, info: ResolveInfo,
    ) -> "VerifyAccountMutation":
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


class ResendVerificationEmailMutation(DjangoFormMutation):
    """
    Sends verification email again. Return error if
    a user with the provided email is not found.
    """

    message = graphene.String()

    class Meta:
        form_class = EmailForm

    @classmethod
    def perform_mutate(
        cls, form: EmailForm, info: ResolveInfo,
    ) -> "ResendVerificationEmailMutation":
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


class SendPasswordResetEmailMutation(DjangoFormMutation):
    """
    Send password reset email. For non verified users,
    send an verification email instead. Return error
    if a user with the provided email is not found.
    """

    message = graphene.String()

    class Meta:
        form_class = EmailForm

    @classmethod
    def perform_mutate(
        cls, form: EmailForm, info: ResolveInfo,
    ) -> "SendPasswordResetEmailMutation":
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
        cls, form: EmailForm, info: ResolveInfo,
    ) -> "ResetPasswordMutation":
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
        return cls(user=user, message=Messages.LOGGED_IN)


class ChangePasswordMutation(
    VerificationRequiredMutationMixin, DjangoModelFormMutation
):
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
    def perform_mutate(
        cls, form: ChangePasswordForm, info: ResolveInfo
    ) -> "ChangePasswordMutation":
        assert info.context is not None
        new_password = form.cleaned_data["new_password"]

        get_user_model().objects.set_password(
            user=info.context.user, password=new_password
        )

        return cls(message=Messages.PASSWORD_UPDATED)


class DeleteUserMutation(VerificationRequiredMutationMixin, DjangoModelFormMutation):
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
    def perform_mutate(
        cls, form: DeleteUserForm, info: ResolveInfo
    ) -> "DeleteUserMutation":
        assert info.context is not None
        user = info.context.user
        user.delete()
        return cls(message=Messages.USER_DELETED)


class UpdateUserMutation(
    VerificationRequiredMutationMixin, FileMutationMixin, DjangoModelFormMutation
):
    """Update user model fields. User must be verified."""

    user = graphene.Field(UserObjectType)
    message = graphene.String()

    class Meta:
        form_class = UpdateUserForm
        exclude_fields = ("id",)

    @classmethod
    def perform_mutate(
        cls, form: UpdateUserForm, info: ResolveInfo
    ) -> "UpdateUserMutation":
        assert info.context is not None
        user = info.context.user
        get_user_model().objects.update_user(user, **form.cleaned_data)
        return cls(user=user, message=Messages.USER_UPDATED)


class Query(graphene.ObjectType):
    user = graphene.Field(UserObjectType, id=graphene.ID())
    user_me = graphene.Field(UserObjectType)

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
