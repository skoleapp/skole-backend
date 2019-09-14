from rest_framework.test import APITestCase


class PublicUserAPITests(APITestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_register_success(self):
        pass

    def test_register_error(self):
        pass

    def test_login_success(self):
        pass

    def test_login_error(self):
        pass

    def test_user_list_superuser(self):
        pass

    def test_user_list_not_superuser(self):
        pass

    def test_user_me(self):
        pass

    def test_user_profile(self):
        pass


class PrivateUserAPITests(APITestCase):
    def test_refresh_token_success(self):
        pass

    def test_refresh_token_invalid_token(self):
        pass

    def test_refresh_token_token_does_not_exist(self):
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

    def test_change_password_other(self):
        pass
