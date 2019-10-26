from graphene_django.utils.testing import GraphQLTestCase

from api.schemas.schema import schema
from api.utils import USER_REGISTERED_MESSAGE
from tests.api.utils.user import (
    login_user,
    query_user,
    query_user_list,
    register_one_user,
)


class PublicUserAPITests(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def test_register_success(self):
        content = register_one_user(self)
        assert content["data"]["register"]["errors"] is None
        assert content["data"]["register"]["message"] == USER_REGISTERED_MESSAGE

    def test_register_error(self):
        # bad email
        content = register_one_user(self, email="badmail.com")
        message = content["data"]["register"]["errors"][0]["messages"][0]
        assert message == "Enter a valid email address."

        # too short password
        content = register_one_user(self, password="short")
        message = content["data"]["register"]["errors"][0]["messages"][0]
        assert "Ensure this value has at least" in message

    def test_register_email_not_unique(self):
        register_one_user(self)
        # email already in use
        content = register_one_user(self, username="unique")
        message = content["data"]["register"]["errors"][0]["messages"][0]
        assert message == "User with this Email already exists."

    def test_register_username_not_unique(self):
        register_one_user(self)
        # username already in use
        content = register_one_user(self, email="unique@email.com")
        message = content["data"]["register"]["errors"][0]["messages"][0]
        assert message == "User with this Username already exists."

    def test_login_success(self):
        register_one_user(self)
        # log in with the registered user
        content = login_user(self)
        assert "token" in content["data"]["login"]
        assert content["data"]["login"]["user"]["email"] == "test@test.com"

    def test_login_error(self):
        register_one_user(self)

        # invalid email
        content = login_user(self, email="wrong@email.com")
        message = content["errors"][0]["message"]
        assert message == "Please, enter valid credentials"

        # invalid password
        content = login_user(self, password="wrongpass")
        message = content["errors"][0]["message"]
        assert message == "Please, enter valid credentials"

    def test_user_profile(self):
        register_one_user(self)

        content = query_user_list(self)
        id_ = content["data"]["userList"][0]["id"]
        # get the profile of the registered user
        content = query_user(self, id=id_)
        assert content["data"]["user"]["id"] == id_
        assert content["data"]["user"]["username"] == "testuser"

    def test_user_list(self):
        register_one_user(self)
        register_one_user(self, email="test2@test.com", username="testuser2")
        register_one_user(self, email="test3@test.com", username="testuser3")

        # check that the register users come as a result for the user list
        content = query_user_list(self)
        assert len(content["data"]["userList"]) == 3
        assert content["data"]["userList"][0]["username"] == "testuser"
        assert content["data"]["userList"][1]["username"] == "testuser2"
        assert content["data"]["userList"][2]["username"] == "testuser3"


class PrivateUserAPITests(GraphQLTestCase):
    def setUp(self):
        # self.user = sample_user()
        # self.user2 = sample_user(
        #     username="othertestuser",
        #     email="othertest@test.com",
        # )
        # self.client.force_authenticate(user=self.user)
        pass

    def tearDown(self):
        # self.user.delete()
        # self.user2.delete()
        pass

    def test_user_me(self):
        pass

    def test_user_me_links_to_own_profile(self):
        pass

    def test_user_profile_own_get(self):
        pass

    def test_user_profile_own_patch(self):
        # test that the data returned to the response is correct

        # test that the data also changed in the profile
        pass

    def test_user_profile_own_put(self):
        # test that the data returned to the response is correct

        # test that the data also changed in the profile
        pass

    def test_user_profile_own_delete(self):
        # test that the profile cannot be found anymore
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
