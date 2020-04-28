from django.contrib.auth import get_user_model
from mypy.types import JsonDict

from skole.tests.utils import SchemaTestCase
from skole.utils.constants import Messages, ValidationErrors


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
            verified
            rank
            badge
            courseCount
            resourceCount
            school {
                id
            }
            subject {
                id
            }
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

    def query_user(self, id: int) -> JsonDict:
        variables = {"id": id}

        # language=GraphQL
        graphql = (
            self.user_fields
            + """
            query User($id: ID!) {
                user(id: $id) {
                    ...userFields
                }
            }
        """
        )
        return self.execute(graphql, variables=variables)["user"]

    def query_user_me(self) -> JsonDict:
        # language=GraphQL
        graphql = (
            self.user_fields
            + """
            query UserMe {
                userMe {
                    ...userFields
                }
            }
        """
        )
        res = self.execute(graphql)
        if self.should_error:
            return res
        return res["userMe"]

    def mutate_register(
        self,
        username: str = "newuser",
        email: str = "newemail@test.com",
        password: str = "password",
        code: str = "TEST",
    ) -> JsonDict:
        return self.execute_input_mutation(
            input_type="RegisterMutationInput!",
            op_name="register",
            input={
                "username": username,
                "email": email,
                "password": password,
                "code": code,
            },
            result="message",
        )

    def mutate_login(
        self, username_or_email: str = "testuser2", password: str = "password"
    ) -> JsonDict:
        return self.execute_input_mutation(
            input_type="LoginMutationInput!",
            op_name="login",
            input={"usernameOrEmail": username_or_email, "password": password},
            result="user { ...userFields } token message",
            fragment=self.user_fields,
        )

    def mutate_update_user(
        self,
        username: str = "testuser2",
        email: str = "testuser2@test.com",
        title: str = "",
        bio: str = "",
        avatar: str = "",
        school: str = "1",
        subject: str = "1",
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
                "school": school,
                "subject": subject,
            },
            result="user { ...userFields } message",
            fragment=self.user_fields,
        )

    def mutate_change_password(
        self, old_password: str = "password", new_password: str = "newpassword"
    ) -> JsonDict:
        return self.execute_input_mutation(
            input_type="ChangePasswordMutationInput!",
            op_name="changePassword",
            input={"oldPassword": old_password, "newPassword": new_password,},
            result="message",
        )

    def mutate_delete_user(self, password: str = "password") -> JsonDict:
        return self.execute_input_mutation(
            input_type="DeleteUserMutationInput!",
            op_name="deleteUser",
            input={"password": password},
            result="message",
        )

    def test_field_fragment(self) -> None:
        self.authenticated = False
        self.assert_field_fragment_matches_schema(self.user_fields)

    def test_register_ok(self) -> None:
        self.authenticated = False

        res = self.mutate_register()
        assert res["errors"] is None
        assert res["message"] == Messages.USER_REGISTERED

    def test_register_error(self) -> None:
        self.authenticated = False

        # Username taken.
        res = self.mutate_register(username="testuser2")
        message = res["errors"][0]["messages"][0]
        assert ValidationErrors.USERNAME_TAKEN == message

        # Email taken.
        res = self.mutate_register(email="testuser2@test.com")
        message = res["errors"][0]["messages"][0]
        assert ValidationErrors.EMAIL_TAKEN == message

        # Invalid beta code.
        res = self.mutate_register(code="invalid")
        message = res["errors"][0]["messages"][0]
        assert message == ValidationErrors.INVALID_BETA_CODE

        # Too short username.
        res = self.mutate_register(username="to")
        message = res["errors"][0]["messages"][0]
        assert "Ensure this value has at least" in message

        # Too short password.
        res = self.mutate_register(password="short")
        message = res["errors"][0]["messages"][0]
        assert "Ensure this value has at least" in message

    def test_login_ok_with_username(self) -> None:
        self.authenticated = False

        res = self.mutate_login()
        assert isinstance(res["token"], str)
        assert res["user"]["email"] == "testuser2@test.com"
        assert res["user"]["username"] == "testuser2"
        assert res["message"] == Messages.LOGGED_IN

    def test_login_ok_with_email(self) -> None:
        self.authenticated = False

        res = self.mutate_login(username_or_email="testuser2@test.com")
        assert isinstance(res["token"], str)
        assert res["user"]["email"] == "testuser2@test.com"
        assert res["user"]["username"] == "testuser2"
        assert res["message"] == Messages.LOGGED_IN

    def test_login_error(self) -> None:
        self.authenticated = False

        # Invalid username.
        res = self.mutate_login(username_or_email="badusername")
        assert res["token"] is None
        assert res["errors"][0]["messages"][0] == ValidationErrors.AUTH_ERROR

        # Invalid email.
        res = self.mutate_login(username_or_email="bademail@test.com")
        assert res["token"] is None
        assert res["errors"][0]["messages"][0] == ValidationErrors.AUTH_ERROR

        # Invalid password.
        res = self.mutate_login(password="wrongpass")
        assert res["token"] is None
        assert res["errors"][0]["messages"][0] == ValidationErrors.AUTH_ERROR

    def test_user(self) -> None:
        # Own user.
        user1 = self.query_user(id=2)
        assert user1["id"] == "2"
        assert user1["username"] == "testuser2"
        assert user1["email"] == "testuser2@test.com"
        assert user1["verified"]
        assert user1["rank"] == "Freshman"
        assert user1["badge"] == "Moderator"
        assert user1["school"] == {"id": "1"}
        assert user1["school"] == {"id": "1"}

        # Random user.
        user2 = self.query_user(id=3)
        assert user2["id"] == "3"
        assert user2["username"] == "testuser3"
        assert user2["email"] == ""
        assert user2["verified"] is None
        assert user2["rank"] == "Tutor"
        assert user2["badge"] is None
        assert user2["school"] is None
        assert user2["school"] is None

        # ID not found.
        assert self.query_user(id=999) is None

    def test_user_me(self) -> None:
        user = self.query_user_me()
        assert user["id"] == "2"
        assert user["username"] == "testuser2"
        assert user["email"] == "testuser2@test.com"
        assert user["verified"]

        # Shouldn't work without auth.
        self.authenticated = False
        self.should_error = True
        res = self.query_user_me()
        assert "permission" in res["errors"][0]["message"]
        assert res["data"] == {"userMe": None}

    def test_update_user_ok(self) -> None:
        # Fine to not change anything.
        user = self.query_user_me()
        res = self.mutate_update_user()
        assert res["errors"] is None
        assert res["user"] == user
        assert res["message"] == Messages.USER_UPDATED

        # Update some fields.
        new_username = "newusername"
        new_email = "newmail@email.com"
        new_title = "My new Title."
        new_bio = "My new bio."
        new_school = "2"
        new_subject = "2"

        res = self.mutate_update_user(
            username=new_username,
            email=new_email,
            title=new_title,
            bio=new_bio,
            school=new_school,
            subject=new_subject,
        )

        assert res["errors"] is None
        assert res["user"]["username"] == new_username
        assert res["user"]["email"] == new_email
        assert res["user"]["title"] == new_title
        assert res["user"]["bio"] == new_bio
        assert res["user"]["school"] == {"id": new_school}
        assert res["user"]["school"] == {"id": new_subject}
        assert res["message"] == Messages.USER_UPDATED

    def test_update_user_error(self) -> None:
        user_old = self.query_user_me()

        # Email is already taken.
        res = self.mutate_update_user(email="root@root.com")
        assert len(res["errors"]) == 1
        assert res["errors"][0]["messages"][0] == ValidationErrors.EMAIL_TAKEN
        assert res["user"] is None

        res = self.mutate_update_user(username="testuser3")
        assert len(res["errors"]) == 1
        assert res["errors"][0]["messages"][0] == ValidationErrors.USERNAME_TAKEN
        assert res["user"] is None

        # Check that nothing has changed.
        assert self.query_user_me() == user_old

    def test_update_user_avatar(self) -> None:
        # TODO: Implement these:
        # Add avatar.
        # Change avatar.
        # Remove avatar.
        pass

    def test_user_delete_ok(self) -> None:
        # Delete the logged in testuser2.
        res = self.mutate_delete_user()
        assert res["errors"] is None
        assert res["message"] == Messages.USER_DELETED

        # Test that the user cannot be found anymore.
        assert get_user_model().objects.filter(pk=2).count() == 0

    def test_user_delete_error(self) -> None:
        # Delete the logged in testuser2.
        res = self.mutate_delete_user(password="wrongpass")
        assert res["errors"][0]["messages"][0] == ValidationErrors.INVALID_PASSWORD

        # Test that the user didn't get deleted.
        assert get_user_model().objects.filter(pk=2).count() == 1

    def test_change_password_ok(self) -> None:
        old_hash = get_user_model().objects.get(pk=2).password
        res = self.mutate_change_password()
        assert res["errors"] is None
        assert res["message"] == Messages.PASSWORD_UPDATED
        new_hash = get_user_model().objects.get(pk=2).password
        assert old_hash != new_hash

    def test_change_password_error(self) -> None:
        res = self.mutate_change_password(old_password="badpass")
        assert res["errors"][0]["messages"][0] == ValidationErrors.INVALID_OLD_PASSWORD
