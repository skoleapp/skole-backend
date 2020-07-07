from typing import Optional

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from mypy.types import JsonDict

from skole.tests.helpers import (
    FileData,
    SkoleSchemaTestCase,
    get_form_error,
    get_graphql_error,
    is_slug_match,
)
from skole.utils.constants import Messages, ValidationErrors
from skole.utils.types import ID


class UserSchemaTests(SkoleSchemaTestCase):
    authenticated_user: Optional[int] = 2

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
            badges {
                id
            }
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
            activity {
                targetUser {
                    id
                    username
                }
                description
            }
        }
    """

    def query_user(self, *, id: ID) -> JsonDict:
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

    def query_user_me(self, assert_error: bool = False) -> JsonDict:
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
        res = self.execute(graphql, assert_error=assert_error)
        if assert_error:
            return res
        return res["userMe"]

    def mutate_register(
        self,
        *,
        username: str = "newuser",
        email: str = "newemail@test.com",
        school: ID = 1,
        subject: ID = 1,
        password: str = "password",
        code: str = "TEST",
    ) -> JsonDict:
        return self.execute_input_mutation(
            input_type="RegisterMutationInput!",
            op_name="register",
            input={
                "username": username,
                "email": email,
                "school": school,
                "subject": subject,
                "password": password,
                "code": code,
            },
            result="message",
        )

    def mutate_login(
        self, *, username_or_email: str = "testuser2", password: str = "password"
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
        *,
        username: str = "testuser2",
        email: str = "testuser2@test.com",
        title: str = "",
        bio: str = "",
        avatar: str = "",
        school: ID = 1,
        subject: ID = 1,
        file_data: FileData = None,
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
            file_data=file_data,
        )

    def mutate_change_password(
        self, *, old_password: str = "password", new_password: str = "newpassword"
    ) -> JsonDict:
        return self.execute_input_mutation(
            input_type="ChangePasswordMutationInput!",
            op_name="changePassword",
            input={"oldPassword": old_password, "newPassword": new_password},
            result="message",
        )

    def mutate_delete_user(self, *, password: str = "password") -> JsonDict:
        return self.execute_input_mutation(
            input_type="DeleteUserMutationInput!",
            op_name="deleteUser",
            input={"password": password},
            result="message",
        )

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.user_fields)

    def test_register_ok(self) -> None:
        self.authenticated_user = None

        res = self.mutate_register()
        assert res["errors"] is None
        assert res["message"] == Messages.USER_REGISTERED

    def test_register_error(self) -> None:
        self.authenticated_user = None

        # Username taken.
        res = self.mutate_register(username="testuser2")
        assert ValidationErrors.USERNAME_TAKEN == get_form_error(res)

        # Email taken.
        res = self.mutate_register(email="testuser2@test.com")
        assert ValidationErrors.EMAIL_TAKEN == get_form_error(res)

        # Invalid beta code.
        res = self.mutate_register(code="invalid")
        assert get_form_error(res) == ValidationErrors.INVALID_BETA_CODE

        # Too short username.
        res = self.mutate_register(username="to")
        assert "Ensure this value has at least" in get_form_error(res)

        # Too short password.
        res = self.mutate_register(password="short")
        assert "Ensure this value has at least" in get_form_error(res)

    def test_login_ok_with_username(self) -> None:
        self.authenticated_user = None

        res = self.mutate_login()
        assert isinstance(res["token"], str)
        assert res["user"]["email"] == "testuser2@test.com"
        assert res["user"]["username"] == "testuser2"
        assert res["message"] == Messages.LOGGED_IN

    def test_login_ok_with_email(self) -> None:
        self.authenticated_user = None

        res = self.mutate_login(username_or_email="testuser2@test.com")
        assert isinstance(res["token"], str)
        assert res["user"]["email"] == "testuser2@test.com"
        assert res["user"]["username"] == "testuser2"
        assert res["message"] == Messages.LOGGED_IN

    def test_login_error(self) -> None:
        self.authenticated_user = None

        # Invalid username.
        res = self.mutate_login(username_or_email="badusername")
        assert res["token"] is None
        assert get_form_error(res) == ValidationErrors.AUTH_ERROR

        # Invalid email.
        res = self.mutate_login(username_or_email="bademail@test.com")
        assert res["token"] is None
        assert get_form_error(res) == ValidationErrors.AUTH_ERROR

        # Invalid password.
        res = self.mutate_login(password="wrongpass")
        assert res["token"] is None
        assert get_form_error(res) == ValidationErrors.AUTH_ERROR

    def test_user(self) -> None:
        # Own user.
        user1 = self.query_user(id=2)
        assert user1["id"] == "2"
        assert user1["username"] == "testuser2"
        assert user1["email"] == "testuser2@test.com"
        assert user1["verified"]
        assert user1["rank"] == "Freshman"
        assert user1["school"] == {"id": "1"}
        assert user1["subject"] == {"id": "1"}
        assert len(user1["badges"]) == 0
        assert len(user1["votes"]) == 1
        assert len(user1["createdCourses"]) == 4
        assert len(user1["createdResources"]) == 1
        assert len(user1["starredCourses"]) == 0
        assert len(user1["starredResources"]) == 0
        assert len(user1["activity"]) == 4

        # Some other user.
        user2 = self.query_user(id=3)
        assert user2["id"] == "3"
        assert user2["username"] == "testuser3"
        assert user2["email"] == "" # Private field.
        assert user2["verified"] is None # Private field.
        assert user2["rank"] == "Tutor"
        assert user2["school"] is None # Private field.
        assert len(user2["badges"]) == 0
        assert len(user2["votes"]) == 1
        assert len(user2["createdCourses"]) == 4
        assert len(user2["createdResources"]) == 0
        assert user2["starredCourses"] is None # Private field.
        assert user2["starredResources"] is None # Private field.
        assert user2["activity"] is None # Private field.

        # ID not found.
        assert self.query_user(id=999) is None

    def test_user_me(self) -> None:
        user = self.query_user_me()
        assert user["id"] == "2"
        assert user["username"] == "testuser2"
        assert user["email"] == "testuser2@test.com"
        assert user["verified"]
        assert user["rank"] == "Freshman"
        assert user["school"] == {"id": "1"}
        assert user["subject"] == {"id": "1"}
        assert len(user["badges"]) == 0
        assert len(user["votes"]) == 1
        assert len(user["createdCourses"]) == 4
        assert len(user["createdResources"]) == 1
        assert len(user["starredCourses"]) == 0
        assert len(user["starredResources"]) == 0
        assert len(user["activity"]) == 4

        # Shouldn't work without auth.
        self.authenticated_user = None
        res = self.query_user_me(assert_error=True)
        assert "permission" in get_graphql_error(res)
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
        res = self.mutate_update_user(email="admin@admin.com")
        assert len(res["errors"]) == 1
        assert get_form_error(res) == ValidationErrors.EMAIL_TAKEN
        assert res["user"] is None

        res = self.mutate_update_user(username="testuser3")
        assert len(res["errors"]) == 1
        assert get_form_error(res) == ValidationErrors.USERNAME_TAKEN
        assert res["user"] is None

        # Check that nothing has changed.
        assert self.query_user_me() == user_old

    def test_update_user_avatar(self) -> None:
        file_path = "media/uploads/avatars/test_avatar.jpg"
        # No avatar at the beginning.
        assert self.query_user_me()["avatar"] == ""

        # Set an avatar.
        with open(file_path, "rb") as f:
            avatar = UploadedFile(f)
            res = self.mutate_update_user(file_data=[("avatar", avatar)])

        file_url = res["user"]["avatar"]
        assert is_slug_match(file_path, file_url)
        assert self.query_user_me()["avatar"] == file_url

        # Update some other fields, avatar should stay when sending the old value.
        new_title = "new title"
        new_bio = "new bio"
        res = self.mutate_update_user(title=new_title, bio=new_bio, avatar=file_url)
        assert is_slug_match(file_path, res["user"]["avatar"])
        assert res["user"]["title"] == new_title
        assert res["user"]["bio"] == new_bio

        # Setting avatar to some random value shouldn't change it,
        # and it also shouldn't give any errors.
        res = self.mutate_update_user(avatar="badvalue")
        assert res["errors"] is None
        assert is_slug_match(file_path, res["user"]["avatar"])

        # Delete the avatar.
        assert get_user_model().objects.get(pk=2).avatar
        res = self.mutate_update_user(avatar="")
        assert res["user"]["avatar"] == ""
        assert self.query_user_me()["avatar"] == ""
        assert not get_user_model().objects.get(pk=2).avatar

    def test_delete_user_ok(self) -> None:
        # Delete the logged in testuser2.
        res = self.mutate_delete_user()
        assert res["errors"] is None
        assert res["message"] == Messages.USER_DELETED

        # Test that the user cannot be found anymore.
        assert get_user_model().objects.filter(pk=2).count() == 0

    def test_delete_user_error(self) -> None:
        # Delete the logged in testuser2.
        res = self.mutate_delete_user(password="wrongpass")
        assert get_form_error(res) == ValidationErrors.INVALID_PASSWORD

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
        assert get_form_error(res) == ValidationErrors.INVALID_OLD_PASSWORD
