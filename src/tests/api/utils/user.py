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


def sample_register_op_name_input_data(**params):
    input_data = {"email": "test@test.com", "username": "testuser", "password": "password"}

    if params is not None:
        input_data.update(**params)

    return "register", input_data


sample_register_mutation = \
    """
    mutation register($input: RegisterMutationInput!) {
     register(input: $input) {
       user {
         id
         username
         email
       }
     }
    }
    """
