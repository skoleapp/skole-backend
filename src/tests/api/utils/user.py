from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse

USER_LIST_API_URL = reverse("user-list")
USER_ME_API_URL = reverse("user-detail", args=["me"])
CHANGE_LANGUAGE_API_URL = reverse("user-change-language")
CHANGE_PASSWORD_API_URL = reverse("user-change-password")
LOGIN_API_URL = reverse("user-login")
REGISTER_API_URL = reverse("user-register")


def user_detail_api_url(user_id):
    return reverse("user-detail", args=[user_id])


def sample_user_payload(**params):
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


def sample_user(**params):
    defaults = {
        "email": "test@test.com",
        "first_name": "test",
        "last_name": "test",
        "is_vendor": False,
        "password": "password"
    }

    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)
