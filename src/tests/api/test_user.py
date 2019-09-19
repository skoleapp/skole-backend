from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from api.utils import LANGUAGE_SET_SUCCESSFULLY_MESSAGE, USER_REGISTERED_SUCCESSFULLY_MESSAGE
from core.utils import ENGLISH, SWEDISH
from .utils.user import (
    CHANGE_PASSWORD_API_URL,
    LOGIN_API_URL,
    REGISTER_API_URL,
    USER_LIST_API_URL,
    USER_ME_API_URL,
    sample_user_register_payload,
    sample_user_patch_payload,
    user_detail_api_url,
    sample_user, sample_user_put_payload)


class PublicUserAPITests(APITestCase):
    def test_register_success(self):
        payload = sample_user_register_payload()
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_201_CREATED
        assert res.data["message"] == USER_REGISTERED_SUCCESSFULLY_MESSAGE

    def test_register_error(self):
        # bad email
        payload = sample_user_register_payload(email="badmail.com")
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

        # too short password
        payload = sample_user_register_payload(password="short", confirm_password="short")
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

        # password != confirm_password
        payload = sample_user_register_payload(password="password", confirm_password="password1")
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_email_not_unique(self):
        # email already in use
        payload = sample_user_register_payload()
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_201_CREATED
        payload["username"] = "unique username"
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_username_not_unique(self):
        # username already in use
        payload = sample_user_register_payload()
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_201_CREATED
        payload["email"] = "unique@email.com"
        res = self.client.post(REGISTER_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self):
        # register one user
        self.client.post(REGISTER_API_URL, sample_user_register_payload())

        # log in with that user
        payload = {
            "username_or_email": "testuser",
            "password": "password",
        }
        res = self.client.post(LOGIN_API_URL, payload)
        assert res.status_code == status.HTTP_200_OK
        assert "token" in res.data

    def test_login_error(self):
        # register one user
        self.client.post(REGISTER_API_URL, sample_user_register_payload())

        # invalid username
        payload = {
            "username_or_email": "badusername",
            "password": "password",
        }
        res = self.client.post(LOGIN_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

        # invalid email
        payload = {
            "username_or_email": "bademail@mail.com",
            "password": "password",
        }
        res = self.client.post(LOGIN_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

        # invalid password
        payload = {
            "username_or_email": "testuser",
            "password": "badpass",
        }
        res = self.client.post(LOGIN_API_URL, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_profile(self):
        # register one user
        user = get_user_model().objects.create_user(**sample_user_register_payload())

        # get the profile of that user
        res = self.client.get(user_detail_api_url(user.id))
        assert res.status_code == status.HTTP_200_OK
        assert res.data["username"] == "testuser"
        assert res.data["title"] is None
        assert "email" not in res.data

    def test_user_me(self):
        res = self.client.get(USER_ME_API_URL)
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_user_list(self):
        # register one user
        user = get_user_model().objects.create_user(**sample_user_register_payload())

        # check that the user comes as a result for user list
        res = self.client.get(USER_LIST_API_URL)
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data["results"]) == 1
        assert res.data["results"][0]["username"] == "testuser"


class PrivateUserAPITests(APITestCase):
    def setUp(self):
        self.user = sample_user()
        self.user2 = sample_user(
            username="othertestuser",
            email="othertest@test.com",
        )
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        self.user.delete()
        self.user2.delete()

    def test_user_me_links_to_own_profile(self):
        res1 = self.client.get(user_detail_api_url(user_id="me"))
        res2 = self.client.get(USER_ME_API_URL)
        assert res1.status_code == status.HTTP_200_OK
        assert res2.status_code == status.HTTP_200_OK
        assert res1.data == res2.data

    def test_user_profile_own_get(self):
        res = self.client.get(user_detail_api_url(user_id="me"))
        assert res.status_code == 200
        assert res.data["username"] == self.user.username
        assert res.data["email"] == self.user.email
        assert res.data["title"] is None
        assert res.data["bio"] is None
        assert res.data["points"] == 0
        assert res.data["language"] == "ENGLISH"

    def test_user_profile_own_patch(self):
        payload = sample_user_patch_payload()

        # test that the data returned to the response is correct
        res = self.client.patch(user_detail_api_url(user_id="me"), payload)
        assert res.status_code == 200
        assert res.data["title"] == "Nice Title for the User"
        assert res.data["bio"] == "Same text for the bio."

        # test that the data also changed in the profile
        res = self.client.get(user_detail_api_url(user_id="me"))
        assert res.data["title"] == "Nice Title for the User"
        assert res.data["bio"] == "Same text for the bio."

    def test_user_profile_own_put(self):
        payload = sample_user_put_payload()

        # test that the data returned to the response is correct
        res = self.client.put(user_detail_api_url(user_id="me"), payload)
        assert res.status_code == 200
        assert res.data["username"] == "newusername"
        assert res.data["email"] == "newemail@mail.com"
        assert res.data["title"] == "Nice Title for the User"
        assert res.data["bio"] == "Same text for the bio."
        assert res.data["language"] == SWEDISH

        # test that the data also changed in the profile
        res = self.client.get(user_detail_api_url(user_id="me"))
        assert res.data["username"] == "newusername"

    def test_user_profile_own_delete(self):
        res = self.client.delete(user_detail_api_url(user_id="me"))
        assert res.status_code == status.HTTP_204_NO_CONTENT

        # test that the profile cannot be found anymore
        res = self.client.get(user_detail_api_url(user_id="me"))
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_user_profile_other_patch(self):
        res = self.client.patch(user_detail_api_url(user_id=self.user2.id), {})
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_user_profile_other_put(self):
        res = self.client.put(user_detail_api_url(user_id=self.user2.id), {})
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_user_profile_other_delete(self):
        res = self.client.delete(user_detail_api_url(user_id=self.user2.id))
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_change_password_success(self):
        payload = {
            "old_password": "password",
            "password": "new pass",
            "confirm_password": "new pass",
        }
        res = self.client.post(CHANGE_PASSWORD_API_URL, payload)
        assert res.status_code == status.HTTP_200_OK

    def test_change_password_error(self):
        pass

