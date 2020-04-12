from mypy.types import JsonDict

from api.utils.messages import AUTH_ERROR_MESSAGE
from tests.utils import BaseSchemaTestCase, execute_input_mutation


class UserSchemaTestCase(BaseSchemaTestCase):
    authenticated = True

    fields = """
    id
    username
    title
    bio
    avatar
    created
    email
    score
    avatar
    avatarThumbnail
    courseCount
    resourceCount
    createdCourses {
      id
    }
    createdResources {
      id
    }
    votes {
      id
    }
    starredCourses {
      id
    }
    starredResources {
      id
    }
    """

    def query_users(self) -> JsonDict:
        query = f"""
          {{
            users {{
              {self.fields}
            }}
          }}
        """
        return self.execute(query)["users"]

    def query_user(self, id: int) -> JsonDict:
        variables = {"id": id}

        query = f"""
          query ($id: ID!) {{
            user(id: $id) {{
              {self.fields}
            }}
          }}
        """
        return self.execute(query, variables=variables)["user"]

    def query_user_me(self) -> JsonDict:
        query = f"""
          {{
            userMe {{
              {self.fields}
            }}
          }}
        """
        return self.execute(query)["userMe"]

    def mutate_register(self, **params: str) -> JsonDict:
        input = {"username": "newuser", "password": "password", "code": "ABC00001"}

        return execute_input_mutation(
            self,
            "RegisterMutationInput!",
            "register",
            input,
            f"user {{ {self.fields} }}",
            **params,
        )

    def mutate_login(self, **params: str) -> JsonDict:
        input = {"username": "testuser2", "password": "password"}

        return execute_input_mutation(
            self,
            "LoginMutationInput!",
            "login",
            input,
            f"user {{ {self.fields} }} token",
            **params,
        )

    def mutate_update_user(self, **params: str) -> JsonDict:
        input_data = {
            "username": "testuser",
            "email": "test@test.com",
            "title": "",
            "bio": "",
            "avatar": "",
            "language": "English",
        }

        if params is not None:
            input_data.update(**params)

        mutation = f"""
          mutation updateUser($input: UpdateUserMutationInput!) {{
            updateUser(input: $input) {{
              errors {{
                field
                messages
              }}
              user {{
                {self.fields}
              }}
            }}
          }}
        """

        return self.query(mutation, variables={"input": input_data})

    def mutate_change_password(self, **params: str) -> JsonDict:
        input = {
            "oldPassword": "password",
            "newPassword": "newpassword",
        }

        if params is not None:
            input.update(**params)

        mutation = f"""
          mutation ($input: ChangePasswordMutationInput!) {{
            changePassword(input: $input) {{
              errors {{
                field
                messages
              }}
              user {{
                {self.fields}
              }}
            }}
          }}
        """

        return self.query(mutation, variables={"input": input})

    def mutate_delete_user(self, **params: str) -> JsonDict:
        input = {
            "password": "password",
        }

        if params is not None:
            input.update(**params)

        mutation = f"""
          mutation ($input: DeleteUserMutationInput!) {{
            deleteUser(input: $input) {{
              errors {{
                field
                messages
              }}
              message
            }}
          }}
        """
        return self.query(mutation, variables={"input": input})

    def test_register_ok(self) -> None:
        res = self.mutate_register()
        assert res["errors"] is None
        assert res["user"] is not None

    def test_register_error(self) -> None:
        # too short username
        res = self.mutate_register(username="to")
        assert res["user"] is None
        message = res["errors"][0]["messages"][0]
        assert "too short" in message

        # too short password
        res = self.mutate_register(password="short")
        assert res["user"] is None
        message = res["errors"][0]["messages"][0]
        assert "Ensure this value has at least" in message

    def test_register_email_not_unique(self) -> None:
        self.mutate_register()
        # email already in use
        res = self.mutate_register(username="unique")
        cont = res["data"]["register"]
        message = cont["errors"][0]["messages"][0]
        assert message == "User with this Email already exists."

    def test_register_username_not_unique(self) -> None:
        self.mutate_register()
        # username already in use
        res = self.mutate_register(email="unique@email.com")
        cont = res["data"]["register"]
        message = cont["errors"][0]["messages"][0]
        assert message == "User with this Username already exists."

    def test_login_success(self) -> None:
        self.mutate_register()

        # login with the email of the registered user
        res = self.mutate_login_user()
        cont = res["data"]["login"]
        assert "token" in cont
        assert cont["user"]["email"] == "test@test.com"
        assert cont["user"]["username"] == "testuser"

        # login with username
        res = self.mutate_login_user(usernameOrEmail="testuser")
        cont = res["data"]["login"]
        assert "token" in cont
        assert cont["user"]["email"] == "test@test.com"
        assert cont["user"]["username"] == "testuser"

    def test_login_error(self) -> None:
        self.mutate_register()

        # invalid email
        res = self.mutate_login_user(usernameOrEmail="wrong@email.com")
        cont = res["data"]["login"]
        assert cont["errors"][0]["messages"][0] == AUTH_ERROR_MESSAGE

        # invalid password
        res = self.mutate_login_user(password="wrongpass")
        cont = res["data"]["login"]
        assert cont["errors"][0]["messages"][0] == AUTH_ERROR_MESSAGE

    def test_user_detail(self) -> None:
        self.mutate_register()

        # Get the id of the first user, so we can use it to query
        res = self.query_users()
        id = res["data"]["users"][0]["id"]

        # Get the profile with that id
        res = self.query_user(id=id)
        cont = res["data"]["user"]
        assert cont["id"] == id
        assert cont["username"] == "testuser"

        # ID not found
        res = self.query_user(999)
        cont = res["data"]["user"]
        assert cont is None
        assert "does not exist" in res["errors"][0]["message"]

    def test_users(self) -> None:
        self.mutate_register()
        self.mutate_register(email="test2@test.com", username="testuser2")
        self.mutate_register(email="test3@test.com", username="testuser3")

        # check that the register users come as a result for the users
        res = self.query_users()
        cont = res["data"]["users"]
        assert len(cont) == 3
        assert cont[0]["username"] == "testuser"
        assert cont[1]["username"] == "testuser2"
        assert cont[2]["username"] == "testuser3"

    def test_user_me(self) -> None:
        res = self.query_user_me()
        cont = res["data"]["userMe"]
        assert cont["username"] == "testuser"
        assert cont["email"] == "test@test.com"
        assert cont["language"] == "English"

    def test_update_user(self) -> None:
        new_mail = "newmail@email.com"
        new_language = "Swedish"
        res = self.mutate_update_user(email=new_mail, language=new_language)
        cont = res["data"]["updateUser"]
        assert cont["errors"] is None
        assert cont["user"]["email"] == new_mail
        assert cont["user"]["language"] == "Swedish"

    def test_update_user_error(self) -> None:
        res = self.mutate_update_user(language="badlang")
        cont = res["data"]["updateUser"]
        assert "valid choice" in cont["errors"][0]["messages"][0]
        assert cont["user"] is None

    def test_update_user_avatar(self) -> None:
        # TODO: implement
        pass

    def test_user_delete(self) -> None:
        # delete the logged in user
        res = self.mutate_user_delete()
        cont = res["data"]["deleteUser"]
        assert "deleted" in cont["message"]

        # test that the profile cannot be found anymore
        res = self.query_user(id=1)
        assert res["data"]["user"] is None

    def test_change_password_success(self) -> None:
        res = self.mutate_change_password()
        cont = res["data"]["changePassword"]
        assert cont["errors"] is None
        assert cont["user"]["id"] is not None
        assert cont["user"]["modified"] is not None

    def test_change_password_error(self) -> None:
        res = self.mutate_change_password(oldPassword="badpass")
        cont = res["data"]["changePassword"]
        assert cont["errors"][0]["messages"][0] == "Incorrect old password."
