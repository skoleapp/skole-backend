from ..utils import INCORRECT_OLD_PASSWORD, USER_DELETED_MESSAGE, USER_REGISTERED_MESSAGE
from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoFormMutation
import graphql_jwt
from graphql_extensions.auth.decorators import login_required

class UserTypePublic(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "title", "bio", "points", "created")


class UserTypePrivate(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "title", "bio", "points", "created", "email", "language")

class RegisterForm(forms.ModelForm):
    password = forms.CharField(min_length=settings.PASSWORD_MIN_LENGTH)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password")


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField()
    new_password = forms.CharField(min_length=settings.PASSWORD_MIN_LENGTH)


class RegisterMutation(DjangoFormMutation):
    message = graphene.String()

    class Meta:
        form_class = RegisterForm

    @classmethod
    def perform_mutate(cls, form, info):
        get_user_model().objects.create_user(
            email=form.cleaned_data["email"],
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        return cls(message=USER_REGISTERED_MESSAGE)

class ChangePasswordMutation(DjangoFormMutation):
    class Meta:
        form_class = ChangePasswordForm

    @classmethod
    @login_required
    def perform_mutate(cls, form, info):
        user = get_user_model().objects.get(pk=info.context.user.id)
        
        if user.check_password(form.cleaned_data["old_password"]):
            get_user_model().objects.set_password(user, form.cleaned_data["new_password"])
        else:
            raise ValueError(INCORRECT_OLD_PASSWORD)


class DeleteUserMutation(graphene.Mutation):
    message = graphene.String()

    @login_required
    def mutate(self, info):
        get_user_model().objects.get(pk=info.context.user.id).delete()
        return DeleteUserMutation(message=USER_DELETED_MESSAGE)

    
class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserTypePrivate)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)

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
        return get_user_model().objects.get(pk=info.context.user.id)
        


class Mutation(graphene.ObjectType):
    register = RegisterMutation.Field()
    login = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    change_password = ChangePasswordMutation.Field()
    delete_user = DeleteUserMutation.Field()


# TODO: delete user
# TODO: update user
