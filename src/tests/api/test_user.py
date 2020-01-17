from django.test import RequestFactory
from graphene.test import Client
from graphene_django.utils.testing import GraphQLTestCase

from api.schemas.schema import schema
from api.utils import USER_DELETED_MESSAGE, UNABLE_TO_AUTHENTICATE_MESSAGE
from app.utils import SWEDISH
from tests.api.utils.user import (
    create_sample_user,
    mutate_change_password,
    mutate_login_user,
    mutate_register_one_user,
    mutate_user_delete,
    mutate_update_user,
    query_user,
    query_users,
    query_user_me,
)


class PublicUserAPITests(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def setUp(self) -> None:
        self.client = Client(schema)

    def tearDown(self) -> None:
        del self.client

    def test_register_success(self) -> None:
        res = mutate_register_one_user(self)
        cont = res["data"]["register"]
        assert cont["errors"] is None
        assert cont["user"] is not None

    def test_register_error(self) -> None:
        # bad email
        res = mutate_register_one_user(self, email="badmail.com")
        cont = res["data"]["register"]
        message = cont["errors"][0]["messages"][0]
        assert message == "Enter a valid email address."

        # too short password
        res = mutate_register_one_user(self, password="short")
        cont = res["data"]["register"]
        message = cont["errors"][0]["messages"][0]
        assert "Ensure this value has at least" in message

    def test_register_email_not_unique(self) -> None:
        mutate_register_one_user(self)
        # email already in use
        res = mutate_register_one_user(self, username="unique")
        cont = res["data"]["register"]
        message = cont["errors"][0]["messages"][0]
        assert message == "User with this Email already exists."

    def test_register_username_not_unique(self) -> None:
        mutate_register_one_user(self)
        # username already in use
        res = mutate_register_one_user(self, email="unique@email.com")
        cont = res["data"]["register"]
        message = cont["errors"][0]["messages"][0]
        assert message == "User with this Username already exists."

    def test_login_success(self) -> None:
        mutate_register_one_user(self)

        # login with the email of the registered user
        res = mutate_login_user(self)
        cont = res["data"]["login"]
        assert "token" in cont
        assert cont["user"]["email"] == "test@test.com"
        assert cont["user"]["username"] == "testuser"

        # login with username
        res = mutate_login_user(self, usernameOrEmail="testuser")
        cont = res["data"]["login"]
        assert "token" in cont
        assert cont["user"]["email"] == "test@test.com"
        assert cont["user"]["username"] == "testuser"

    def test_login_error(self) -> None:
        mutate_register_one_user(self)

        # invalid email
        res = mutate_login_user(self, usernameOrEmail="wrong@email.com")
        cont = res["data"]["login"]
        assert cont["errors"][0]["messages"][0] == UNABLE_TO_AUTHENTICATE_MESSAGE

        # invalid password
        res = mutate_login_user(self, password="wrongpass")
        cont = res["data"]["login"]
        assert cont["errors"][0]["messages"][0] == UNABLE_TO_AUTHENTICATE_MESSAGE

    def test_user_detail(self) -> None:
        mutate_register_one_user(self)

        # Get the id of the first user, so we can use it to query
        res = query_users(self)
        id_ = res["data"]["users"][0]["id"]

        # Get the profile with that id
        res = query_user(self, id_=id_)
        cont = res["data"]["user"]
        assert cont["id"] == id_
        assert cont["username"] == "testuser"

        # ID not found
        res = query_user(self, 999)
        cont = res["data"]["user"]
        assert cont is None
        assert "does not exist" in res["errors"][0]["message"]

    def test_users(self) -> None:
        mutate_register_one_user(self)
        mutate_register_one_user(self, email="test2@test.com", username="testuser2")
        mutate_register_one_user(self, email="test3@test.com", username="testuser3")

        # check that the register users come as a result for the users
        res = query_users(self)
        cont = res["data"]["users"]
        assert len(cont) == 3
        assert cont[0]["username"] == "testuser"
        assert cont[1]["username"] == "testuser2"
        assert cont[2]["username"] == "testuser3"


class PrivateUserAPITests(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def setUp(self) -> None:
        self.user1 = create_sample_user()
        self.user2 = create_sample_user(username="testuser2", email="test2@test.com",)

        self.client = Client(schema)

        # Authenticate the user
        self.client.user = self.user1

        # Add the user to the req
        self.req = RequestFactory().get("/")
        self.req.user = self.user1

    def tearDown(self) -> None:
        try:
            self.user1.delete()
        except AssertionError:
            # user deleted in test
            pass
        self.user2.delete()
        del self.client
        del self.req

    def test_user_me(self) -> None:
        res = query_user_me(self)
        cont = res["data"]["userMe"]
        assert cont["username"] == "testuser"
        assert cont["email"] == "test@test.com"
        assert cont["language"] == "English"

    def test_update_user(self) -> None:
        new_mail = "newmail@email.com"
        new_language = SWEDISH
        res = mutate_update_user(self, email=new_mail, language=new_language)
        cont = res["data"]["updateUser"]
        assert cont["errors"] is None
        assert cont["user"]["email"] == new_mail
        assert cont["user"]["language"] == "Swedish"

    def test_update_user_error(self) -> None:
        res = mutate_update_user(self, language="badlang")
        cont = res["data"]["updateUser"]
        assert "valid choice" in cont["errors"][0]["messages"][0]
        assert cont["user"] is None

    def test_update_user_avatar(self) -> None:
        # TODO: implement
        pass

    def test_user_delete(self) -> None:
        # delete the logged in user
        res = mutate_user_delete(self)
        cont = res["data"]["deleteUser"]
        assert cont["message"] == USER_DELETED_MESSAGE

        # test that the profile cannot be found anymore
        res = query_user(self, id_=1)
        assert res["data"]["user"] is None

    def test_change_password_success(self) -> None:
        res = mutate_change_password(self)
        cont = res["data"]["changePassword"]
        assert cont["errors"] is None
        assert cont["user"]["id"] is not None
        assert cont["user"]["modified"] is not None

    def test_change_password_error(self) -> None:
        res = mutate_change_password(self, oldPassword="badpass")
        cont = res["data"]["changePassword"]
        assert cont["errors"][0]["messages"][0] == "Incorrect old password."
