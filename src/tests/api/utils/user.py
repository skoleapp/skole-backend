import json

from django.contrib.auth import get_user_model

from core.utils import SWEDISH


def sample_user_register_payload(**params):
    defaults = {
        "email": "test@test.com",
        "username": "testuser",
        "password": {
            "password": "password",
            "confirm_password": "password",
        }
    }

    defaults.update(params)
    return defaults


def sample_user_patch_payload(**params):
    defaults = {
        "title": "Nice Title for the User",
        "bio": "Same text for the bio.",
    }

    defaults.update(params)
    return defaults


def sample_user_put_payload(**params):
    defaults = {
        "username": "newusername",
        "email": "newemail@mail.com",
        "title": "Nice Title for the User",
        "bio": "Same text for the bio.",
        "language": SWEDISH,
    }

    defaults.update(params)
    return defaults


def sample_user(**params):
    defaults = {
        "email": "test@test.com",
        "username": "testuser",
        "password": "password",
    }
    defaults.update(params)
    user = get_user_model().objects.create_user(**defaults)
    return user


def register_one_user(test_cls_instance, **params):
    op_name = "register"
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
           message
         }
        }
        """

    res = test_cls_instance.query(
        mutation,
        op_name=op_name,
        input_data=input_data
    )
    return json.loads(res.content)


def login_user(test_cls_instance, **params):
    op_name = "login"
    variables = {"email": "test@test.com", "password": "password"}

    if params is not None:
        variables.update(**params)

    mutation = \
        """
        mutation login($email: String!, $password: String!) {
         login(email: $email, password: $password) {
           token
           user {
             email
           }
         }
        }
        """

    res = test_cls_instance.query(
        mutation,
        op_name=op_name,
        variables=variables,
    )
    return json.loads(res.content)


def query_user(test_cls_instance, **params):
    op_name = "user"
    variables = {"id": 1}

    if params is not None:
        variables.update(**params)

    query = \
        """
        query user($id: Int!) {
         user(id: $id) {
           id
           username
         }
        }
        """

    res = test_cls_instance.query(
        query,
        op_name=op_name,
        variables=variables,
    )
    return json.loads(res.content)


def query_user_list(test_cls_instance):
    op_name = "user"

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

    res = test_cls_instance.query(
        query,
        op_name=op_name,
    )
    return json.loads(res.content)
