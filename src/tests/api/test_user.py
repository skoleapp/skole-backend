from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from .utils.user import (
    CHANGE_LANGUAGE_API_URL,
    CHANGE_PASSWORD_API_URL,
    LOGIN_API_URL,
    REGISTER_API_URL,
    USER_LIST_API_URL,
    USER_ME_API_URL,
    sample_user_payload,
    user_detail_api_url,
)


class PublicUserAPITests(APITestCase):
    def test_register_success(self):
        payload = sample_user_payload()
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_201_CREATED
        assert res.data == {
            "email": "test@test.com",
            "username": "testuser",
        }

    def test_register_error(self):
        # bad email
        payload = sample_user_payload(email="badmail.com")
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

        # too short password
        payload = sample_user_payload(password="short", confirm_password="short")
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

        # password != confirm_password
        payload = sample_user_payload(password="password", confirm_password="password1")
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_email_not_unique(self):
        # email already in use
        payload = sample_user_payload()
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_201_CREATED
        payload["username"] = "unique username"
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_username_not_unique(self):
        # username already in use
        payload = sample_user_payload()
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_201_CREATED
        payload["email"] = "unique@email.com"
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self):
        # FIXME: this doesn't pass
        # register one user
        user = get_user_model().objects.create_user(**sample_user_payload())

        # try to log in with that user
        payload = {
            "username_or_email": "testuser",
            "password": "password",
        }
        res = self.client.post(LOGIN_API_URL, payload)
        assert res.status_code == status.HTTP_200_OK

    def test_login_error(self):
        payload = {
            "username_or_email": "badusername",
            "password": "wrongpass",
        }
        res = self.client.post(LOGIN_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_profile(self):
        pass


class PrivateUserAPITests(APITestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_user_me_links_to_own_profile(self):
        pass

    def test_user_profile_own_get(self):
        pass

    def test_user_profile_own_patch(self):
        pass

    def test_user_profile_own_put(self):
        pass

    def test_user_profile_own_delete(self):
        pass

    def test_user_profile_other_patch(self):
        pass

    def test_user_profile_other_put(self):
        pass

    def test_user_profile_other_delete(self):
        pass

    def test_change_password_success(self):
        pass

    def test_change_password_error(self):
        pass

    def test_user_list_superuser(self):
        pass

    def test_user_list_not_superuser(self):
        pass

