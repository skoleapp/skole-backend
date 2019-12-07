from typing import List, Any, Optional

import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation
from graphene_django.types import ErrorType
from graphql import ResolveInfo
from graphql_extensions.auth.decorators import login_required
from graphql_jwt.decorators import token_auth
from mypy.types import JsonDict

from api.forms.user import LoginForm, RegisterForm, ChangePasswordForm, UpdateUserForm, DeleteUserForm
from api.utils.messages import USER_DELETED_MESSAGE
from api.utils.points import get_points_for_user
from app.models import User, Course, Resource


class UserType(DjangoObjectType):
    email = graphene.String()
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
            "avatar_thumbnail",
            "points",
            "created",
            "created_courses",
            "created_resources"
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


class RegisterMutation(DjangoModelFormMutation):
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


class LoginMutation(DjangoModelFormMutation):
    token = graphene.String()

    class Meta:
        form_class = LoginForm

    @classmethod
    def mutate_and_get_payload(cls, root: Any, info: ResolveInfo, **input: JsonDict) -> 'LoginMutation':
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
    def perform_mutate(cls, root: Any, info: ResolveInfo, user: User, **kwargs: JsonDict) -> 'LoginMutation':
        return cls(user=user)


class ChangePasswordMutation(DjangoModelFormMutation):
    class Meta:
        form_class = ChangePasswordForm

    @classmethod
    def get_form_kwargs(cls, root: Any, info: ResolveInfo, **input: JsonDict) -> JsonDict:
        return {"data": input, "instance": info.context.user}

    @classmethod
    @login_required
    def perform_mutate(cls, form: ChangePasswordForm, info: ResolveInfo) -> 'ChangePasswordMutation':
        return cls(user=info.context.user)


class DeleteUserMutation(DjangoModelFormMutation):
    message = graphene.String()

    class Meta:
        form_class = DeleteUserForm

    @classmethod
    def get_form_kwargs(cls, root: Any, info: ResolveInfo, **input: JsonDict) -> JsonDict:
        return {"data": input, "instance": info.context.user}

    @classmethod
    @login_required
    def perform_mutate(cls, form: DeleteUserForm, info: ResolveInfo) -> 'DeleteUserMutation':
        info.context.user.delete()
        return cls(message=USER_DELETED_MESSAGE)


class UpdateUserMutation(DjangoModelFormMutation):
    class Meta:
        form_class = UpdateUserForm

    @classmethod
    def get_form_kwargs(cls, root: Any, info: ResolveInfo, **input: JsonDict) -> JsonDict:
        return {"data": input, "instance": info.context.user}

    @classmethod
    @login_required
    def perform_mutate(cls, form: UpdateUserForm, info: ResolveInfo) -> 'UpdateUserMutation':
        data = form.cleaned_data
        files = info.context.FILES

        if "1" in files:
            data["avatar"] = files["1"]  # Overwrite form value with actual image.

        user = info.context.user
        get_user_model().objects.update_user(user, **data)
        return cls(user=user)


class Query(graphene.ObjectType):
    leaderboard = graphene.List(UserType)
    user = graphene.Field(UserType, user_id=graphene.Int(required=True))
    user_me = graphene.Field(UserType)

    def resolve_leaderboard(self, info: ResolveInfo) -> List[User]:
        """
        Return 100 users with the most points. Need to handle the sorting
        with Python since the ORM has no idea about the point resolvers.
        """
        return sorted(
            get_user_model().objects.filter(is_superuser=False),
            key = lambda u: get_points_for_user(u), reverse=True
        )[:100]

    def resolve_user(self, info: ResolveInfo, user_id: int) -> User:
        return get_user_model().objects.filter(is_superuser=False).get(pk=user_id)

    @login_required
    def resolve_user_me(self, info: ResolveInfo) -> User:
        return info.context.user


class Mutation(graphene.ObjectType):
    register = RegisterMutation.Field()
    login = LoginMutation.Field()
    update_user = UpdateUserMutation.Field()
    change_password = ChangePasswordMutation.Field()
    delete_user = DeleteUserMutation.Field()
