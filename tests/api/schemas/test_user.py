from typing import Optional

from mypy.types import JsonDict

from api.utils.messages import AUTH_ERROR_MESSAGE
from tests.test_utils import SchemaTestCase


class UserSchemaTests(SchemaTestCase):
    authenticated = True

    # language=GraphQL
    user_fields = """
        fragment userFields on UserObjectType {
            id
            username
            email
            score
            title
            bio
            avatar
            avatarThumbnail
            created
            courseCount
            resourceCount
            votes {
                id
            }
            createdCourses {
                id
            }
            createdResources {
                id
            }
            starredCourses {
                id
            }
            starredResources {
                id
            }
        }
    """

    def query_users(
        self,
        page: int = 1,
        page_size: int = 10,
        username: Optional[str] = None,
        ordering: Optional[str] = None,
    ) -> JsonDict:
        variables = {
            "page": page,
            "pageSize": page_size,
            "username": username,
            "ordering": ordering,
        }

        # language=GraphQL
        graphql = (
            self.user_fields
            + """
            query Users($page: Int, $pageSize: Int, $username: String, $ordering: String) {
                users(page: $page, pageSize: $pageSize, username: $username, ordering: $ordering) {
                    count
                    page
                    pages
                    hasNext
                    hasPrev
                    objects {
                      ...userFields
                    }
                }
            }
        """
        )
        return self.execute(graphql, variables=variables)["users"]

    def query_user(self, id: int) -> JsonDict:
        variables = {"id": id}

        # language=GraphQL
        graphql = (
            self.user_fields
            + """
            query User ($id: ID!) {
                user(id: $id) {
                    ...userFields
                }
            }
        """
        )
        return self.execute(graphql, variables=variables)["user"]

    def query_user_me(self, should_error: bool = False) -> JsonDict:
        # language=GraphQL
        graphql = (
            self.user_fields
            + """
            query UserMe {
                userMe {
                    id
                    ...userFields
                }
            }
        """
        )
        res = self.execute(graphql, should_error=should_error)
        if should_error:
            return res
        return res["userMe"]

    def mutate_register(
        self,
        username: str = "newuser",
        password: str = "password",
        code: str = "ABC00001",
    ) -> JsonDict:
        return self.execute_input_mutation(
            input_type="RegisterMutationInput!",
            op_name="register",
            input={"username": username, "password": password, "code": code},
            result="user { ...userFields }",
            fragment=self.user_fields,
        )

    def mutate_login(
        self, username: str = "testuser2", password: str = "password"
    ) -> JsonDict:
        return self.execute_input_mutation(
            input_type="LoginMutationInput!",
            op_name="login",
            input={"username": username, "password": password},
            result="user { ...userFields } token",
            fragment=self.user_fields,
        )

    def mutate_update_user(
        self,
        username: str = "testuser2",
        email: str = "test2@test.com",
        title: str = "",
        bio: str = "",
        avatar: str = "",
    ) -> JsonDict:
        return self.execute_input_mutation(
            input_type="UpdateUserMutationInput!",
            op_name="updateUser",
            input={
                "username": username,
                "email": email,
                "title": title,
                "bio": bio,
                "avatar": avatar,
            },
            result="user { ...userFields }",
            fragment=self.user_fields,
        )

    '''
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
    '''

    def test_register_ok(self) -> None:
        self.authenticated = False

        res = self.mutate_register()
        assert res["errors"] is None
        assert res["user"]["username"] == "newuser"
        assert res["user"]["email"] == ""

    def test_register_error(self) -> None:
        self.authenticated = False

        # Username taken.
        res = self.mutate_register(username="testuser2")
        assert res["user"] is None
        message = res["errors"][0]["messages"][0]
        assert "This username is taken." == message

        # Invalid beta code.
        res = self.mutate_register(code="invalid")
        assert res["user"] is None
        message = res["errors"][0]["messages"][0]
        assert message == "Invalid beta register code."

        # Too short username.
        res = self.mutate_register(username="to")
        assert res["user"] is None
        message = res["errors"][0]["messages"][0]
        assert "Ensure this value has at least" in message

        # Too short password.
        res = self.mutate_register(password="short")
        assert res["user"] is None
        message = res["errors"][0]["messages"][0]
        assert "Ensure this value has at least" in message

    def test_login_ok(self) -> None:
        self.authenticated = False

        res = self.mutate_login()
        assert isinstance(res["token"], str)
        assert res["user"]["email"] == "test2@test.com"
        assert res["user"]["username"] == "testuser2"

    def test_login_error(self) -> None:
        self.authenticated = False

        # Trying to login with email.
        res = self.mutate_login(username="test2@test.com")
        assert res["token"] is None
        assert res["errors"][0]["messages"][0] == AUTH_ERROR_MESSAGE

        # Invalid username.
        res = self.mutate_login(username="badusername")
        assert res["token"] is None
        assert res["errors"][0]["messages"][0] == AUTH_ERROR_MESSAGE

        # Invalid password.
        res = self.mutate_login(password="wrongpass")
        assert res["token"] is None
        assert res["errors"][0]["messages"][0] == AUTH_ERROR_MESSAGE

    def test_user(self) -> None:
        user = self.query_user(id=2)
        assert user["id"] == "2"
        assert user["username"] == "testuser2"

        # ID not found.
        assert self.query_user(id=999) is None

    def test_users(self) -> None:
        # Default ordering is lexicographic (=not numeric!) by username.
        users = self.query_users(page_size=999)
        assert len(users["objects"]) == 11
        assert users["objects"][0]["username"] == "testuser10"
        assert users["objects"][9]["username"] == "testuser8"
        assert users["objects"][10]["username"] == "testuser9"

        # Change page size.
        users = self.query_users(page_size=3)
        assert len(users["objects"]) == 3

        # Get second page.
        users = self.query_users(page_size=3, page=2)
        assert len(users["objects"]) == 3
        assert users["page"] == 2
        assert users["objects"][0]["username"] == "testuser2"

        # Can't see emails of the users.
        users = self.query_users(page_size=999)
        assert any(user["email"] != "" for user in users["objects"])

    def test_user_me(self) -> None:
        user = self.query_user_me()
        assert user["id"] == "2"
        assert user["username"] == "testuser2"
        assert user["email"] == "test2@test.com"

        # Doesn't work without auth.
        self.authenticated = False
        res = self.query_user_me(should_error=True)
        assert "permission" in res["errors"][0]["message"]
        assert res["data"] == {"userMe": None}

    def test_update_user(self) -> None:
        # Fine to not change anything.
        res = self.mutate_update_user()
        user = self.query_user_me()
        assert res["errors"] is None
        assert res["user"] == user

        # Update some fields.
        new_username = "newusername"
        new_email = "newmail@email.com"
        new_title = "My new Title."
        res = self.mutate_update_user(
            username=new_username, email=new_email, title=new_title
        )
        assert res["errors"] is None
        assert res["user"]["username"] == new_username
        assert res["user"]["email"] == new_email
        assert res["user"]["title"] == new_title
        assert res["user"]["bio"] == ""

        # Email is already taken.
        res = self.mutate_update_user(email="test3@test.com")
        assert res["errors"] is not None
        assert res["user"] is None

    """

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
    """
