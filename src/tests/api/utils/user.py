import json

from django.contrib.auth import get_user_model
from graphene_django.utils import GraphQLTestCase
from mypy.types import JsonDict

from core.models import User
from core.utils import ENGLISH


def create_sample_user(**params: str) -> User:
    defaults = {
        "email": "test@test.com",
        "username": "testuser",
        "password": "password",
    }
    defaults.update(params)
    user = get_user_model().objects.create_user(**defaults)
    return user


def mutate_register_one_user(test_cls: GraphQLTestCase, **params: str) -> JsonDict:
    input_data = {"email": "test@test.com", "username": "testuser", "password": "password"}

    if params is not None:
        input_data.update(**params)

    mutation = \
        """
        mutation register($input: RegisterMutationInput!) {
          register(input: $input) {
            errors {
              field
              messages
            }
            user {
              id
              created
            }
          }
        }
        """

    return test_cls.client.execute(
        mutation,
        variables={"input": input_data},
    )


def mutate_login_user(test_cls: GraphQLTestCase, **params: str) -> JsonDict:
    input_data = {"usernameOrEmail": "test@test.com", "password": "password"}

    if params is not None:
        input_data.update(**params)

    mutation = \
        """
          mutation login($input: LoginMutationInput!) {
          login(input: $input) {
            errors {
              field
              messages
            }
            token
            user {
              id
              username
              email
              title
              bio
              avatar
              points
              language
            }
          }
        }
        """

    # graphql_jwt somehow doesn't work with client.execute(), so we need to use query().
    res = test_cls.query(
        mutation,
        input_data=input_data,
        op_name="login"
    )
    return json.loads(res.content)


def query_user(test_cls: GraphQLTestCase, id_: int = 1) -> JsonDict:
    variables = {"id": id_}

    query = \
        """
        query user($id: Int!) {
         user(id: $id) {
           id
           username
           title
           bio
           avatar
           points
         }
        }
        """

    return test_cls.client.execute(
        query,
        variables=variables,
    )


def query_user_list(test_cls: GraphQLTestCase) -> JsonDict:
    query = \
        """
        query {
          userList {
            id
            username
            title
            bio
            avatar
            points
          }
        }
        """

    return test_cls.client.execute(
        query,
    )


def mutate_update_user(test_cls: GraphQLTestCase, **params: str) -> JsonDict:
    input_data = {
        "username": "testuser",
        "email": "test@test.com",
        "title": "",
        "bio": "",
        "avatar": "",
        "language": ENGLISH,
    }

    if params is not None:
        input_data.update(**params)

    mutation = \
        """
        mutation updateUser($input: UpdateUserMutationInput!) {
          updateUser(input: $input) {
            errors {
              field
              messages
            }
            user {
              id
              username
              email
              title
              bio
              avatar
              points
              language
            }
          }
        }
        """

    return test_cls.client.execute(
        mutation,
        variables={"input": input_data},
        context_value=test_cls.req,
    )


def query_user_me(test_cls: GraphQLTestCase) -> JsonDict:
    query = \
        """
        query {
          userMe {
            id
            username
            email
            title
            bio
            avatar
            points
            language
          }
        }
        """
    return test_cls.client.execute(
        query,
        context_value=test_cls.req,
    )


def mutate_change_password(test_cls: GraphQLTestCase, **params: str) -> JsonDict:
    input_data = {
        "oldPassword": "password",
        "newPassword": "newpassword",
    }

    if params is not None:
        input_data.update(**params)

    mutation = \
        """
        mutation changePassword($input: ChangePasswordMutationInput!) {
          changePassword(input: $input) {
            errors {
              field
              messages
            }
            user {
              id
              modified
            }
          }
        }
        """

    return test_cls.client.execute(
        mutation,
        variables={"input": input_data},
        context_value=test_cls.req,
    )


def mutate_user_delete(test_cls: GraphQLTestCase) -> JsonDict:
    mutation = \
        """
        mutation {
          deleteUser {
            message
          }
        }
        """
    return test_cls.client.execute(
        mutation,
        context_value=test_cls.req,
    )
