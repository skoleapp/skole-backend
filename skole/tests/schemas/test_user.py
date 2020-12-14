from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail

from skole.tests.helpers import (
    TEST_AVATAR_JPG,
    UPLOADED_AVATAR_JPG,
    FileData,
    SkoleSchemaTestCase,
    get_form_error,
    get_graphql_error,
    get_token_from_email,
    is_slug_match,
    open_as_file,
)
from skole.types import ID, JsonDict
from skole.utils.constants import Messages, MutationErrors, ValidationErrors


class UserSchemaTests(SkoleSchemaTestCase):  # pylint: disable=too-many-public-methods
    authenticated_user: ID = 2

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
            unreadActivityCount
            badges {
                id
                name
            }
            school {
                id
            }
            subject {
                id
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
        return self.execute(graphql, variables=variables)

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
        return self.execute(graphql, assert_error=assert_error)

    def mutate_register(
        self,
        *,
        username: str = "newuser",
        email: str = "newemail@test.com",
        password: str = "somenewpassword",
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="register",
            input_type="RegisterMutationInput!",
            input={"username": username, "email": email, "password": password},
            result="successMessage",
        )

    def mutate_login(
        self, *, username_or_email: str = "testuser2", password: str = "password"
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="login",
            input_type="LoginMutationInput!",
            input={"usernameOrEmail": username_or_email, "password": password},
            result="user { ...userFields } successMessage",
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
            name="updateUser",
            input_type="UpdateUserMutationInput!",
            input={
                "username": username,
                "email": email,
                "title": title,
                "bio": bio,
                "avatar": avatar,
                "school": school,
                "subject": subject,
            },
            result="user { ...userFields } successMessage",
            fragment=self.user_fields,
            file_data=file_data,
        )

    def mutate_change_password(
        self, *, old_password: str = "password", new_password: str = "newpassword1234"
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="changePassword",
            input_type="ChangePasswordMutationInput!",
            input={"oldPassword": old_password, "newPassword": new_password},
            result="successMessage",
        )

    def mutate_delete_user(self, *, password: str = "password") -> JsonDict:
        return self.execute_input_mutation(
            name="deleteUser",
            input_type="DeleteUserMutationInput!",
            input={"password": password},
            result="successMessage",
        )

    def mutate_send_password_reset_email(
        self, *, email: str = "testuser2@test.com"
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="sendPasswordResetEmail",
            input_type="SendPasswordResetEmailMutationInput!",
            input={"email": email},
            result="successMessage",
        )

    def mutate_reset_password(self, *, token: str, new_password: str) -> JsonDict:
        return self.execute_input_mutation(
            name="resetPassword",
            input_type="ResetPasswordMutationInput!",
            input={"token": token, "newPassword": new_password},
            result="successMessage",
        )

    def mutate_verify_account(self, *, token: str) -> JsonDict:
        return self.execute_input_mutation(
            name="verifyAccount",
            input_type="VerifyAccountMutationInput!",
            input={"token": token},
            result="successMessage",
        )

    def mutate_resend_verification_email(self, assert_error: bool = False) -> JsonDict:
        return self.execute_non_input_mutation(
            name="resendVerificationEmail",
            result="successMessage",
            assert_error=assert_error,
        )

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.user_fields)

    def test_register_and_verify_ok(self) -> None:
        self.authenticated_user = None

        assert len(mail.outbox) == 0
        email = "newemail@test.com"
        res = self.mutate_register(email=email)
        assert not res["errors"]
        assert res["successMessage"] == Messages.USER_REGISTERED

        assert len(mail.outbox) == 1
        sent = mail.outbox[0]
        assert sent.from_email == settings.EMAIL_NO_REPLY
        assert sent.to == [email]

        # Username should keep its casing, mut email should be lowercased.
        self.mutate_register(username="MYUSERNAME", email="MAIL@example.COM")
        user = get_user_model().objects.order_by("created").last()
        assert user
        assert user.username == "MYUSERNAME"
        assert user.email == "mail@example.com"

        assert len(mail.outbox) == 2

        sent = mail.outbox[1]
        assert sent.from_email == settings.EMAIL_NO_REPLY
        assert sent.to == ["mail@example.com"]
        assert "Verify" in sent.subject

        res = self.mutate_verify_account(token=get_token_from_email(sent.body))
        assert not res["errors"]
        assert res["successMessage"] == Messages.ACCOUNT_VERIFIED

    def test_register_error(self) -> None:
        self.authenticated_user = None

        # Username taken.
        res = self.mutate_register(username="testuser2")
        assert ValidationErrors.USERNAME_TAKEN == get_form_error(res)

        # Username taken with different casing.
        res = self.mutate_register(username="TESTUSER2")
        assert ValidationErrors.USERNAME_TAKEN == get_form_error(res)

        # Invalid characters in username.
        res = self.mutate_register(username="@testuser")
        assert ValidationErrors.INVALID_USERNAME == get_form_error(res)

        # Email taken.
        res = self.mutate_register(email="testuser2@test.com")
        assert ValidationErrors.EMAIL_TAKEN == get_form_error(res)

        # Email taken with different casing.
        res = self.mutate_register(email="TESTUSER2@test.com")
        assert ValidationErrors.EMAIL_TAKEN == get_form_error(res)

        # Too short username.
        res = self.mutate_register(username="to")
        assert "Ensure this value has at least" in get_form_error(res)

        # Too short password.
        res = self.mutate_register(password="short")
        assert "too short" in get_form_error(res)

        # Too common password.
        res = self.mutate_register(password="superman123")
        assert "too common" in get_form_error(res)

        # Too long password.
        res = self.mutate_register(password="a" * 129)
        assert "Ensure this value has at most" in get_form_error(res)

        # Password cannot be entirely numeric.
        res = self.mutate_register(password="0123456789101213")
        assert "numeric" in get_form_error(res)

        # Password cannot be too similar to username.
        res = self.mutate_register(password="newuser")
        assert "too similar to the username" in get_form_error(res)

        # Password cannot be too similar to email.
        res = self.mutate_register(password="email")
        assert "too similar to the email" in get_form_error(res)

    def test_verify_error(self) -> None:
        res = self.mutate_verify_account(token="badtoken")
        assert res["errors"] == MutationErrors.INVALID_TOKEN_VERIFY
        assert len(mail.outbox) == 0

        # Can't verify testuser2 since it's already verified.
        res = self.mutate_resend_verification_email()
        assert res["errors"] == MutationErrors.ALREADY_VERIFIED

        self.authenticated_user = None
        res = self.mutate_resend_verification_email(assert_error=True)
        assert "permission" in get_graphql_error(res)

    def test_resend_verification_email(self) -> None:
        self.authenticated_user = 3  # Not yet verified.
        res = self.mutate_resend_verification_email()
        assert not res["errors"]

        assert len(mail.outbox) == 1
        sent = mail.outbox[0]
        assert sent.from_email == settings.EMAIL_NO_REPLY
        assert sent.to == ["testuser3@test.com"]
        assert "Verify" in sent.subject

        # Works with the token that was sent in the email.
        res = self.mutate_verify_account(token=get_token_from_email(sent.body))
        assert not res["errors"]
        assert res["successMessage"] == Messages.ACCOUNT_VERIFIED

    def test_login_ok_with_username(self) -> None:
        self.authenticated_user = None

        res = self.mutate_login()
        assert res["user"]["email"] == "testuser2@test.com"
        assert res["user"]["username"] == "testuser2"
        assert res["successMessage"] == Messages.LOGGED_IN

    def test_login_ok_with_email(self) -> None:
        self.authenticated_user = None

        res = self.mutate_login(username_or_email="testuser2@test.com")
        assert res["user"]["email"] == "testuser2@test.com"
        assert res["user"]["username"] == "testuser2"
        assert res["successMessage"] == Messages.LOGGED_IN

    def test_login_error(self) -> None:
        self.authenticated_user = None

        # Invalid username.
        res = self.mutate_login(username_or_email="badusername")
        assert get_form_error(res) == ValidationErrors.AUTH_ERROR

        # Invalid email.
        res = self.mutate_login(username_or_email="bademail@test.com")
        assert get_form_error(res) == ValidationErrors.AUTH_ERROR

        # Invalid password.
        res = self.mutate_login(password="wrongpass")
        assert get_form_error(res) == ValidationErrors.AUTH_ERROR

    def test_register_and_login(self) -> None:
        self.authenticated_user = None

        username = "newuser2"
        email = "newemail2@test.com"
        password = "asupersecurepassword"
        res = self.mutate_register(username=username, email=email, password=password)
        assert not res["errors"]
        assert res["successMessage"] == Messages.USER_REGISTERED

        # Login with email.
        res = self.mutate_login(username_or_email=email, password=password)
        assert not res["errors"]
        assert res["user"]["email"] == email
        assert res["user"]["username"] == username
        assert res["successMessage"] == Messages.LOGGED_IN

        # Login with username.
        res = self.mutate_login(username_or_email=username, password=password)
        assert not res["errors"]
        assert res["user"]["email"] == email
        assert res["user"]["username"] == username
        assert res["successMessage"] == Messages.LOGGED_IN

    def test_user(self) -> None:
        # Own user.
        user1 = self.query_user(id=2)
        assert user1["id"] == "2"
        assert user1["username"] == "testuser2"
        assert user1["email"] == "testuser2@test.com"
        assert user1["verified"]
        assert user1["rank"] == "Freshman"
        assert user1["unreadActivityCount"] == 3
        assert user1["school"] == {"id": "1"}
        assert user1["subject"] == {"id": "1"}
        assert len(user1["badges"]) == 1

        # Some other user.
        user2 = self.query_user(id=3)
        assert user2["id"] == "3"
        assert user2["username"] == "testuser3"
        assert len(user2["badges"]) == 1
        assert user2["badges"][0]["name"] == "Tester"
        assert user2["rank"] == "Tutor"
        assert user2["unreadActivityCount"] is None  # Private field.
        assert user2["email"] is None  # Private field.
        assert user2["verified"] is None  # Private field.
        assert user2["school"] is None  # Private field.

        # ID not found.
        assert self.query_user(id=999) is None

    def test_user_me(self) -> None:
        user = self.query_user_me()
        assert user["id"] == "2"
        assert user["username"] == "testuser2"
        assert user["email"] == "testuser2@test.com"
        assert user["verified"]
        assert user["rank"] == "Freshman"
        assert user["unreadActivityCount"] == 3
        assert user["school"] == {"id": "1"}
        assert user["subject"] == {"id": "1"}
        assert len(user["badges"]) == 1
        assert user["badges"][0]["name"] == "Tester"

        # Shouldn't work without auth.
        self.authenticated_user = None
        res = self.query_user_me(assert_error=True)
        assert "permission" in get_graphql_error(res)
        assert res["data"] == {"userMe": None}

    def test_update_user_ok(self) -> None:
        # Fine to not change anything.
        user = self.query_user_me()
        res = self.mutate_update_user()
        assert not res["errors"]
        assert res["user"] == user
        assert res["successMessage"] == Messages.USER_UPDATED

        # User is currently verified.
        current_user = self.get_authenticated_user()
        assert current_user.verified

        # Changing the email should unverify the user, and lowercase the email.
        res = self.mutate_update_user(email="NEWMAIL@email.com")
        assert res["user"]["email"] == "newmail@email.com"
        current_user.refresh_from_db()
        assert not current_user.verified

        # Update some fields.
        new_username = "newusername"
        new_title = "My new Title."
        new_bio = "My new bio."
        new_school = "2"
        new_subject = "2"

        res = self.mutate_update_user(
            username=new_username,
            title=new_title,
            bio=new_bio,
            school=new_school,
            subject=new_subject,
        )

        assert not res["errors"]
        assert res["user"]["username"] == new_username
        assert res["user"]["title"] == new_title
        assert res["user"]["bio"] == new_bio
        assert res["user"]["school"] == {"id": new_school}
        assert res["user"]["school"] == {"id": new_subject}
        assert res["successMessage"] == Messages.USER_UPDATED

    def test_update_user_error(self) -> None:
        user_old = self.query_user_me()

        # Email is already taken.
        res = self.mutate_update_user(email="admin@admin.com")
        assert len(res["errors"]) == 1
        assert get_form_error(res) == ValidationErrors.EMAIL_TAKEN
        assert res["user"] is None

        # Same email with different casing is already taken.
        res = self.mutate_update_user(email="ADMIN@admin.com")
        assert len(res["errors"]) == 1
        assert get_form_error(res) == ValidationErrors.EMAIL_TAKEN
        assert res["user"] is None

        # Username is already taken.
        res = self.mutate_update_user(username="testuser3")
        assert len(res["errors"]) == 1
        assert get_form_error(res) == ValidationErrors.USERNAME_TAKEN
        assert res["user"] is None

        # Invalid characters in username.
        res = self.mutate_update_user(username="test-user")
        assert ValidationErrors.INVALID_USERNAME == get_form_error(res)

        # Same username with different casing is already taken.
        res = self.mutate_update_user(username="TESTUSER3")
        assert len(res["errors"]) == 1
        assert get_form_error(res) == ValidationErrors.USERNAME_TAKEN
        assert res["user"] is None

        # Check that nothing has changed.
        assert self.query_user_me() == user_old

    def test_update_user_avatar(self) -> None:
        # No avatar at the beginning.
        assert self.query_user_me()["avatar"] == ""

        # Set an avatar.
        with open_as_file(TEST_AVATAR_JPG) as avatar:
            res = self.mutate_update_user(file_data=[("avatar", avatar)])
        file_url = res["user"]["avatar"]
        assert is_slug_match(UPLOADED_AVATAR_JPG, file_url)
        assert self.query_user_me()["avatar"] == file_url

        # Update some other fields, avatar should stay when sending the old value.
        new_title = "new title"
        new_bio = "new bio"
        res = self.mutate_update_user(title=new_title, bio=new_bio, avatar=file_url)
        assert is_slug_match(UPLOADED_AVATAR_JPG, res["user"]["avatar"])
        assert res["user"]["title"] == new_title
        assert res["user"]["bio"] == new_bio

        # Setting avatar to some random value shouldn't change it,
        # and it also shouldn't give any errors.
        res = self.mutate_update_user(avatar="badvalue")
        assert not res["errors"]
        assert is_slug_match(UPLOADED_AVATAR_JPG, res["user"]["avatar"])

        # Delete the avatar.
        assert self.get_authenticated_user().avatar
        res = self.mutate_update_user(avatar="")
        assert res["user"]["avatar"] == ""
        assert self.query_user_me()["avatar"] == ""
        assert not self.get_authenticated_user().avatar

    def test_delete_user_ok(self) -> None:
        old_count = get_user_model().objects.count()

        # Delete the logged in testuser2.
        res = self.mutate_delete_user()
        assert not res["errors"]
        assert res["successMessage"] == Messages.USER_DELETED

        # Test that the user cannot be found anymore.
        assert not get_user_model().objects.filter(pk=2)
        assert get_user_model().objects.count() == old_count - 1

    def test_delete_user_error(self) -> None:
        old_count = get_user_model().objects.count()

        # Delete the logged in testuser2.
        res = self.mutate_delete_user(password="wrongpass")
        assert get_form_error(res) == ValidationErrors.INVALID_PASSWORD

        # Test that the user didn't get deleted.
        assert get_user_model().objects.filter(pk=2)
        assert get_user_model().objects.count() == old_count

    def test_change_password_ok(self) -> None:
        old_hash = self.get_authenticated_user().password
        res = self.mutate_change_password()
        assert not res["errors"]
        assert res["successMessage"] == Messages.PASSWORD_UPDATED
        user = self.get_authenticated_user()
        assert old_hash != user.password
        assert user.check_password("newpassword1234")

    def test_change_password_error(self) -> None:
        # Invalid old password.
        res = self.mutate_change_password(old_password="badpass")
        assert get_form_error(res) == ValidationErrors.INVALID_OLD_PASSWORD

        # Can't change password to an invalid one:

        # Too short password.
        res = self.mutate_change_password(new_password="short")
        assert "too short" in get_form_error(res)

        # Too common password.
        res = self.mutate_change_password(new_password="superman123")
        assert "too common" in get_form_error(res)

        # Too long password.
        res = self.mutate_change_password(new_password="a" * 129)
        assert "Ensure this value has at most" in get_form_error(res)

        # Password cannot be entirely numeric.
        res = self.mutate_change_password(new_password="0123456789101213")
        assert "numeric" in get_form_error(res)

        # Password cannot be too similar to username.
        res = self.mutate_change_password(new_password="testuser2")
        assert "too similar to the username" in get_form_error(res)

        # Password cannot be too similar to email.
        res = self.mutate_change_password(new_password="testuser2@test.com")
        assert "too similar to the email" in get_form_error(res)

    def test_reset_password_ok(self) -> None:
        email = "testuser2@test.com"
        res = self.mutate_send_password_reset_email(email=email)
        assert not res["errors"]
        assert res["successMessage"] == Messages.PASSWORD_RESET_EMAIL_SENT

        assert len(mail.outbox) == 1
        sent = mail.outbox[0]
        assert sent.from_email == settings.EMAIL_NO_REPLY
        assert sent.to == [email]
        assert "Reset your password" in sent.subject

        new_password = "some_new_password"
        res = self.mutate_reset_password(
            token=get_token_from_email(sent.body),
            new_password=new_password,
        )
        assert not res["errors"]
        user = self.get_authenticated_user()
        assert user.check_password(new_password)

    def test_reset_password_error(self) -> None:
        self.mutate_send_password_reset_email()
        token = get_token_from_email(mail.outbox[0].body)

        # Email not found.
        user = self.get_authenticated_user()
        user.verified = False
        user.save()
        res = self.mutate_send_password_reset_email(email="foobar@test.com")
        assert res["errors"] == MutationErrors.USER_NOT_FOUND_WITH_EMAIL

        # Can't reset password to an invalid one:

        # Too short password.
        res = self.mutate_reset_password(token=token, new_password="short")
        assert "too short" in get_form_error(res)

        # Too common password.
        res = self.mutate_reset_password(token=token, new_password="superman123")
        assert "too common" in get_form_error(res)

        # Too long password.
        res = self.mutate_reset_password(token=token, new_password="a" * 129)
        assert "Ensure this value has at most" in get_form_error(res)

        # Password cannot be entirely numeric.
        res = self.mutate_reset_password(token=token, new_password="0123456789101213")
        assert "numeric" in get_form_error(res)

        # Password cannot be too similar to username.
        res = self.mutate_reset_password(token=token, new_password="testuser2")
        assert "too similar to the username" in get_form_error(res)

        # Password cannot be too similar to email.
        res = self.mutate_reset_password(token=token, new_password="testuser2@test.com")
        assert "too similar to the email" in get_form_error(res)
