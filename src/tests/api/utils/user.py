import json

from django.contrib.auth import get_user_model

from core.utils import ENGLISH


def create_sample_user(**params):
    defaults = {
        "email": "test@test.com",
        "username": "testuser",
        "password": "password",
    }
    defaults.update(params)
    user = get_user_model().objects.create_user(**defaults)
    return user


def mutate_register_one_user(test_cls_instance, **params):
    input_data = {"email": "test@test.com", "username": "testuser", "password": "password"}

    if params is not None:
        input_data.update(**params)

    mutation = \
        """
        mutation register($input: RegisterMutationInput!) {
          register(input: $input) {
            errors {
              messages
            }
            user {
              id
              created
            }
          }
        }
        """

    return test_cls_instance.client.execute(
        mutation,
        variables={"input": input_data},
    )


def mutate_login_user(test_cls_instance, **params):
    variables = {"email": "test@test.com", "password": "password"}

    if params is not None:
        variables.update(**params)

    mutation = \
        """
        mutation login($email: String!, $password: String!) {
          login(email: $email, password: $password) {
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
    res = test_cls_instance.query(
        mutation,
        variables=variables,
        op_name="login"
    )
    return json.loads(res.content)


def query_user(test_cls_instance, **params):
    variables = {"id": 1}

    if params is not None:
        variables.update(**params)

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

    return test_cls_instance.client.execute(
        query,
        variables=variables,
    )


def query_user_list(test_cls_instance):
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

    return test_cls_instance.client.execute(
        query,
    )


def mutate_update_user(test_cls_instance, **params):
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

    return test_cls_instance.client.execute(
        mutation,
        variables={"input": input_data},
        context_value=test_cls_instance.req,
    )


def query_user_me(test_cls_instance):
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
    return test_cls_instance.client.execute(
        query,
        context_value=test_cls_instance.req,
    )


def mutate_change_password(test_cls_instance, **params):
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
              messages
            }
            user {
              id
              modified
            }
          }
        }
        """

    return test_cls_instance.client.execute(
        mutation,
        variables={"input": input_data},
        context_value=test_cls_instance.req,
    )


def mutate_user_delete(test_cls_instance):
    mutation = \
        """
        mutation {
          deleteUser {
            message
          }
        }
        """
    return test_cls_instance.client.execute(
        mutation,
        context_value=test_cls_instance.req,
    )
