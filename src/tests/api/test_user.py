import json

from graphene_django.utils.testing import GraphQLTestCase

from api.schemas.schema import schema
from tests.api.utils.user import (
    sample_register_op_name_input_data,
    sample_register_mutation,
)


class PublicUserAPITests(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def test_register_success(self):
        op_name, input_data = sample_register_op_name_input_data()
        res = self.query(
            sample_register_mutation,
            op_name=op_name,
            input_data=input_data
        )
        content = json.loads(res.content)
        self.assertResponseNoErrors(res)
        user = content["data"]["register"]["user"]
        assert "id" in user
        assert user["email"] == "test@test.com"
        assert user["username"] == "testuser"

    def test_register_error(self):
        # bad email

        # too short password

        # password != confirm_password
        pass

    def test_register_email_not_unique(self):
        # email already in use
        pass

    def test_register_username_not_unique(self):
        # username already in use
        pass

    def test_login_success(self):
        # register one user

        # log in with that user
        pass

    def test_login_error(self):
        # register one user

        # invalid username

        # invalid email

        # invalid password
        pass

    def test_user_profile(self):
        # register one user

        # get the profile of that user
        pass

    def test_user_me(self):
        pass

    def test_user_list(self):
        # register one user

        # check that the user comes as a result for user list
        pass


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
