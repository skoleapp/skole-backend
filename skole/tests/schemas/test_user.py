from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import translation
from fcm_django.models import FCMDevice

from skole.models import Badge, BadgeProgress
from skole.tests.helpers import (
    TEST_AVATAR_JPG,
    UPLOADED_AVATAR_JPG,
    FileData,
    SkoleSchemaTestCase,
    get_form_error,
    get_graphql_error,
    get_last,
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
            slug
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
            fcmToken
            commentReplyEmailPermission
            threadCommentEmailPermission
            resourceCommentEmailPermission
            commentReplyPushPermission
            threadCommentPushPermission
            resourceCommentPushPermission
            badges {
                id
                name
                description
                tier
            }
            badgeProgresses {
                badge {
                    id
                    name
                    description
                    tier
                }
                progress
                steps
            }
            selectedBadgeProgress {
                badge {
                    id
                    name
                    description
                    tier
                }
                progress
                steps
            }
            school {
                id
            }
            subject {
                id
            }
        }
    """

    def query_user(self, *, slug: str) -> JsonDict:
        variables = {"slug": slug}

        # language=GraphQL
        graphql = (
            self.user_fields
            + """
            query User($slug: String!) {
                user(slug: $slug) {
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
            input={
                "username": username,
                "email": email,
                "password": password,
            },
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

    def mutate_update_profile(
        self,
        *,
        username: str = "testuser2",
        email: str = "testuser2@test.com",
        title: str = "",
        bio: str = "",
        avatar: str = "uploads/avatars/test_avatar.jpg",
        school: ID = 1,
        subject: ID = 1,
        file_data: FileData = None,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="updateProfile",
            input_type="UpdateProfileMutationInput!",
            input={
                "username": username,
                "title": title,
                "bio": bio,
                "avatar": avatar,
            },
            result="user { ...userFields } successMessage",
            fragment=self.user_fields,
            file_data=file_data,
        )

    def mutate_update_account_settings(
        self,
        *,
        email: str = "testuser2@test.com",
        school: ID = 1,
        subject: ID = 1,
        comment_reply_email_permission: bool = False,
        thread_comment_email_permission: bool = False,
        resource_comment_email_permission: bool = False,
        new_badge_email_permission: bool = False,
        comment_reply_push_permission: bool = True,
        thread_comment_push_permission: bool = True,
        resource_comment_push_permission: bool = True,
        new_badge_push_permission: bool = True,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="updateAccountSettings",
            input_type="UpdateAccountSettingsMutationInput!",
            input={
                "email": email,
                "school": school,
                "subject": subject,
                "commentReplyEmailPermission": comment_reply_email_permission,
                "threadCommentEmailPermission": thread_comment_email_permission,
                "resourceCommentEmailPermission": resource_comment_email_permission,
                "newBadgeEmailPermission": new_badge_email_permission,
                "commentReplyPushPermission": comment_reply_push_permission,
                "threadCommentPushPermission": thread_comment_push_permission,
                "resourceCommentPushPermission": resource_comment_push_permission,
                "newBadgePushPermission": new_badge_push_permission,
            },
            result="user { ...userFields } successMessage",
            fragment=self.user_fields,
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

    def mutate_use_referral_code(self, *, code: str, email: str) -> JsonDict:
        return self.execute_input_mutation(
            name="useReferralCode",
            input_type="UseReferralCodeMutationInput!",
            input={"code": code, "email": email},
            result="successMessage",
        )

    def mutate_resend_verification_email(self, assert_error: bool = False) -> JsonDict:
        return self.execute_non_input_mutation(
            name="resendVerificationEmail",
            result="successMessage",
            assert_error=assert_error,
        )

    def mutate_update_selected_badge(self, badge: ID) -> JsonDict:
        return self.execute_input_mutation(
            name="updateSelectedBadge",
            input_type="UpdateSelectedBadgeMutationInput!",
            input={"id": badge},
            result="badgeProgress { badge { id name } } successMessage",
        )

    def mutate_register_fcm_token(self, *, token: str) -> JsonDict:
        return self.execute_input_mutation(
            name="registerFcmToken",
            input_type="RegisterFCMTokenMutationInput!",
            input={"token": token},
            result="successMessage",
        )

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.user_fields)

    def test_register_ok(self) -> None:
        self.authenticated_user = None

        email = "newemail@test.com"
        res = self.mutate_register(email=email)
        assert not res["errors"]
        assert res["successMessage"] == Messages.USER_REGISTERED
        get_user_model().objects.order_by("created")

        res = self.mutate_register(username="unique", email="unique@test.test")
        assert not res["errors"]
        get_user_model().objects.order_by("created")

        # Username should keep its casing, mut email should be lowercased.
        self.mutate_register(username="MYUSERNAME", email="MAIL@example.COM")
        user = get_last(get_user_model().objects.order_by("created"))
        assert user.username == "MYUSERNAME"
        assert user.email == "mail@example.com"

        # No verification email are sent before referral codes are used.
        assert len(mail.outbox) == 0

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

    def test_use_referral_code_ok(self) -> None:
        email = "newemail@test.com"
        self.mutate_register(email=email)
        assert len(mail.outbox) == 0

        res = self.mutate_use_referral_code(code="TEST1", email=email)
        assert not res["errors"]
        assert res["successMessage"] == Messages.REFERRAL_CODE_SUCCESS
        assert len(mail.outbox) == 1
        sent = mail.outbox[0]
        assert "Verify" in sent.subject
        assert sent.from_email == settings.EMAIL_ADDRESS
        assert sent.to == [email]

    def test_use_referral_code_error(self) -> None:
        email = "newemail@test.com"
        self.mutate_register(email=email)

        # Invalid referral code.
        res = self.mutate_use_referral_code(code="INVALID", email=email)
        assert get_form_error(res) == ValidationErrors.REFERRAL_CODE_INVALID

        # No account for the email.
        res = self.mutate_use_referral_code(code="TEST1", email="invalid@test.test")
        assert get_form_error(res) == ValidationErrors.EMAIL_DOES_NOT_EXIST

        assert len(mail.outbox) == 0  # No verification emails sent.

    def test_verify_ok(self) -> None:
        email = "newemail@test.com"
        self.mutate_register(email=email)
        self.mutate_use_referral_code(code="TEST1", email=email)

        assert len(mail.outbox) == 1
        sent = mail.outbox[0]
        res = self.mutate_verify_account(token=get_token_from_email(sent.body))
        assert not res["errors"]
        assert res["successMessage"] == Messages.ACCOUNT_VERIFIED

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
        assert sent.from_email == settings.EMAIL_ADDRESS
        assert sent.to == ["testuser3@test.com"]
        assert "Verify" in sent.subject
        assert "http://localhost:3001/verify-account" in sent.body

        # Test that the language appears correctly in the urls.
        with translation.override("fi"):
            self.mutate_resend_verification_email()
        assert len(mail.outbox) == 2
        sent = mail.outbox[1]
        assert "http://localhost:3001/fi/verify-account" in sent.body
        with translation.override("sv"):
            self.mutate_resend_verification_email()
        assert len(mail.outbox) == 3
        sent = mail.outbox[2]
        assert "http://localhost:3001/sv/verify-account" in sent.body
        with translation.override("en"):
            self.mutate_resend_verification_email()
        assert len(mail.outbox) == 4
        sent = mail.outbox[3]
        assert "http://localhost:3001/verify-account" in sent.body

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

        # Username is not case sensitive on login.
        res = self.mutate_login(username_or_email="TestUSER2")
        assert res["user"]["email"] == "testuser2@test.com"
        assert res["user"]["username"] == "testuser2"
        assert res["successMessage"] == Messages.LOGGED_IN

    def test_login_ok_with_email(self) -> None:
        self.authenticated_user = None

        res = self.mutate_login(username_or_email="testuser2@test.com")
        assert res["user"]["email"] == "testuser2@test.com"
        assert res["user"]["username"] == "testuser2"
        assert res["successMessage"] == Messages.LOGGED_IN

        # Email is not case sensitive on login.
        res = self.mutate_login(username_or_email="TESTUSER2@test.COM")
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

        self.mutate_use_referral_code(code="TEST1", email=email)

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
        slug = "testuser2"
        user1 = self.query_user(slug=slug)
        assert user1["id"] == "2"
        assert user1["username"] == "testuser2"
        assert user1["slug"] == slug
        assert user1["email"] == "testuser2@test.com"
        assert user1["verified"]
        assert user1["rank"] == "Freshman"
        assert user1["unreadActivityCount"] == 4
        assert user1["fcmToken"] is None
        assert user1["school"] == {"id": "1"}
        assert user1["subject"] == {"id": "1"}
        assert len(user1["badges"]) == 1
        assert len(user1["badgeProgresses"]) == 5
        assert user1["badgeProgresses"][0]["badge"]["id"] == "3"
        assert user1["badgeProgresses"][0]["badge"]["name"] == "First Comment"
        assert user1["badgeProgresses"][0]["progress"] == 0
        assert user1["badgeProgresses"][0]["steps"] == 1

        # Some other user.
        slug = "testuser3"
        user2 = self.query_user(slug=slug)
        assert user2["id"] == "3"
        assert user2["username"] == "testuser3"
        assert user2["slug"] == slug
        assert user2["rank"] == "Tutor"
        assert len(user2["badges"]) == 0
        assert user2["badgeProgresses"] is None  # Private field.
        assert user2["unreadActivityCount"] is None  # Private field.
        assert user2["fcmToken"] is None  # Private field.
        assert user2["email"] is None  # Private field.
        assert user2["verified"] is None  # Private field.
        assert user2["school"] is None  # Private field.

        # Slug not found.
        assert self.query_user(slug="not-found") is None

    def test_user_me(self) -> None:
        user = self.query_user_me()
        assert user["id"] == "2"
        assert user["username"] == "testuser2"
        assert user["slug"] == "testuser2"
        assert user["email"] == "testuser2@test.com"
        assert user["verified"]
        assert user["rank"] == "Freshman"
        assert user["unreadActivityCount"] == 4
        assert user["fcmToken"] is None
        assert user["school"] == {"id": "1"}
        assert user["subject"] == {"id": "1"}
        assert len(user["badges"]) == 1
        assert user["badges"][0]["name"] == "Staff"
        assert len(user["badgeProgresses"]) == 5

        # `badgeProgresses` should be sorted by their completion percentage.
        assert user["badgeProgresses"][0]["badge"]["name"] == "First Comment"
        badge_progress = BadgeProgress.objects.get(badge__identifier="first_upvote")
        badge_progress.badge.steps = 10
        badge_progress.progress = 9
        badge_progress.save()
        user = self.query_user_me()
        assert user["badgeProgresses"][0]["badge"]["name"] == "First Upvote"
        assert user["badgeProgresses"][1]["badge"]["name"] == "First Comment"

        # Shouldn't work without auth.
        self.authenticated_user = None
        res = self.query_user_me(assert_error=True)
        assert "permission" in get_graphql_error(res)
        assert res["data"] == {"userMe": None}

    def test_update_profile(self) -> None:
        # Fine to not change anything.
        user = self.query_user_me()
        res = self.mutate_update_profile()
        assert not res["errors"]
        assert res["user"] == user
        assert res["successMessage"] == Messages.PROFILE_UPDATED

        # User is currently verified.
        current_user = self.get_authenticated_user()
        assert current_user.verified

        # Update some fields.
        new_username = "newusername"
        new_title = "My new Title."
        new_bio = "My new bio."

        res = self.mutate_update_profile(
            username=new_username,
            title=new_title,
            bio=new_bio,
        )

        assert not res["errors"]
        assert res["user"]["username"] == new_username
        assert res["user"]["slug"] == new_username
        assert res["user"]["title"] == new_title
        assert res["user"]["bio"] == new_bio
        assert res["successMessage"] == Messages.PROFILE_UPDATED

        user_old = self.query_user_me()

        # Username is already taken.
        res = self.mutate_update_profile(username="testuser3")
        assert len(res["errors"]) == 1
        assert get_form_error(res) == ValidationErrors.USERNAME_TAKEN
        assert res["user"] is None

        # Invalid characters in username.
        res = self.mutate_update_profile(username="test-user")
        assert ValidationErrors.INVALID_USERNAME == get_form_error(res)

        # Same username with different casing is already taken.
        res = self.mutate_update_profile(username="TESTUSER3")
        assert len(res["errors"]) == 1
        assert get_form_error(res) == ValidationErrors.USERNAME_TAKEN
        assert res["user"] is None

        # Check that nothing has changed.
        assert self.query_user_me() == user_old

    def test_update_avatar(self) -> None:
        # Avatar at the beginning.
        assert self.query_user_me()["avatar"]

        # Delete the avatar.
        assert self.get_authenticated_user().avatar
        res = self.mutate_update_profile(avatar="")
        assert res["user"]["avatar"] == ""
        assert self.query_user_me()["avatar"] == ""
        assert not self.get_authenticated_user().avatar

        # Set an avatar.
        with open_as_file(TEST_AVATAR_JPG) as avatar:
            res = self.mutate_update_profile(file_data=[("avatar", avatar)])
        assert not res["errors"]
        file_url = res["user"]["avatar"]
        assert is_slug_match(UPLOADED_AVATAR_JPG, file_url)
        assert self.query_user_me()["avatar"] == file_url

        # Update some other fields, avatar should stay when sending the old value.
        new_title = "new title"
        new_bio = "new bio"
        res = self.mutate_update_profile(title=new_title, bio=new_bio, avatar=file_url)
        assert is_slug_match(UPLOADED_AVATAR_JPG, res["user"]["avatar"])
        assert res["user"]["title"] == new_title
        assert res["user"]["bio"] == new_bio

        # Setting avatar to some random value shouldn't change it,
        # and it also shouldn't give any errors.
        res = self.mutate_update_profile(avatar="badvalue")
        assert not res["errors"]
        assert is_slug_match(UPLOADED_AVATAR_JPG, res["user"]["avatar"])

    def test_update_account_settings(self) -> None:
        # Fine to not change anything.
        user = self.query_user_me()
        res = self.mutate_update_account_settings()
        assert not res["errors"]
        assert res["user"] == user
        assert res["successMessage"] == Messages.ACCOUNT_SETTINGS_UPDATED

        # User is currently verified.
        current_user = self.get_authenticated_user()
        assert current_user.verified

        # Changing the email should unverify the user, and lowercase the email.
        res = self.mutate_update_account_settings(email="NEWMAIL@email.com")
        assert res["user"]["email"] == "newmail@email.com"
        current_user.refresh_from_db()
        assert not current_user.verified

        # Update some fields.
        new_school = "2"
        new_subject = "2"
        comment_reply_email_permission = True
        thread_comment_email_permission = True
        resource_comment_email_permission = True
        comment_reply_push_permission = True
        thread_comment_push_permission = True
        resource_comment_push_permission = True

        res = self.mutate_update_account_settings(
            school=new_school,
            subject=new_subject,
            comment_reply_email_permission=comment_reply_email_permission,
            thread_comment_email_permission=thread_comment_email_permission,
            resource_comment_email_permission=resource_comment_email_permission,
            comment_reply_push_permission=comment_reply_push_permission,
            thread_comment_push_permission=thread_comment_push_permission,
            resource_comment_push_permission=resource_comment_push_permission,
        )

        assert not res["errors"]
        assert res["user"]["school"] == {"id": new_school}
        assert res["user"]["school"] == {"id": new_subject}
        assert res["user"]["commentReplyEmailPermission"]
        assert res["user"]["threadCommentEmailPermission"]
        assert res["user"]["resourceCommentEmailPermission"]
        assert res["user"]["commentReplyPushPermission"]
        assert res["user"]["threadCommentPushPermission"]
        assert res["user"]["resourceCommentPushPermission"]
        assert res["successMessage"] == Messages.ACCOUNT_SETTINGS_UPDATED

        user_old = self.query_user_me()

        # Email is already taken.
        res = self.mutate_update_account_settings(email="admin@admin.com")
        assert len(res["errors"]) == 1
        assert get_form_error(res) == ValidationErrors.EMAIL_TAKEN
        assert res["user"] is None

        # Same email with different casing is already taken.
        res = self.mutate_update_account_settings(email="ADMIN@admin.com")
        assert len(res["errors"]) == 1
        assert get_form_error(res) == ValidationErrors.EMAIL_TAKEN
        assert res["user"] is None

        # Check that nothing has changed.
        assert self.query_user_me() == user_old

    def test_delete_user(self) -> None:
        old_count = get_user_model().objects.count()

        # Test deleting user with wrong password.
        res = self.mutate_delete_user(password="wrongpass")
        assert get_form_error(res) == ValidationErrors.INVALID_PASSWORD

        # Test that the user didn't get deleted.
        assert get_user_model().objects.filter(pk=2)
        assert get_user_model().objects.count() == old_count

        old_count = get_user_model().objects.count()

        # Delete the logged in testuser2.
        res = self.mutate_delete_user()
        assert not res["errors"]
        assert res["successMessage"] == Messages.USER_DELETED

        # Test that the user cannot be found anymore.
        assert not get_user_model().objects.filter(pk=2)
        assert get_user_model().objects.count() == old_count - 1

    def test_change_password(self) -> None:
        # Test that invalid old password fails.
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

        # Test that it works!
        old_hash = self.get_authenticated_user().password
        res = self.mutate_change_password()
        assert not res["errors"]
        assert res["successMessage"] == Messages.PASSWORD_UPDATED
        user = self.get_authenticated_user()
        assert old_hash != user.password
        assert user.check_password("newpassword1234")

    def test_reset_password(self) -> None:
        email = "testuser2@test.com"
        res = self.mutate_send_password_reset_email(email=email)
        assert not res["errors"]
        assert res["successMessage"] == Messages.PASSWORD_RESET_EMAIL_SENT

        assert len(mail.outbox) == 1
        sent = mail.outbox[0]
        assert sent.from_email == settings.EMAIL_ADDRESS
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

        # Email is not case sensitive
        email = "TESTUSER2@TEST.com"
        res = self.mutate_send_password_reset_email(email=email)
        assert not res["errors"]
        assert res["successMessage"] == Messages.PASSWORD_RESET_EMAIL_SENT
        assert len(mail.outbox) == 2

        self.mutate_send_password_reset_email()
        token = get_token_from_email(mail.outbox[0].body)

        # Test that resetting password with a random email fails.
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

    def test_update_selected_badge(self) -> None:
        user = self.get_authenticated_user()
        user.selected_badge_progress = None
        user.save()

        badge = Badge.objects.get(identifier="first_comment")
        res = self.mutate_update_selected_badge(badge=badge.pk)
        assert not res["errors"]
        assert res["successMessage"] == Messages.BADGE_TRACKING_CHANGED
        assert res["badgeProgress"]["badge"]["id"] == str(badge.id)
        assert res["badgeProgress"]["badge"]["name"] == badge.name
        user.refresh_from_db()
        # Ignore: We know that `badge` cannot be `None` here.
        assert user.selected_badge_progress.badge == badge  # type: ignore[attr-defined]

        # Test that cannot set the badge to null.
        res = self.mutate_update_selected_badge(badge=None)
        assert res["errors"] == MutationErrors.BADGE_CANNOT_BE_NULL
        assert res["successMessage"] is None
        assert res["badgeProgress"] is None
        user.refresh_from_db()
        # Ignore: We know that `badge` cannot be `None` here.
        assert user.selected_badge_progress.badge == badge  # type: ignore[attr-defined]

    def test_register_fcm_token(self) -> None:
        # Register new token.

        user = self.get_authenticated_user()
        token = "token"
        res = self.mutate_register_fcm_token(token=token)
        assert not res["errors"]
        assert res["successMessage"] == Messages.FCM_TOKEN_UPDATED
        assert FCMDevice.objects.count() == 1
        FCMDevice.objects.get(user=user, registration_id=token)

        # Register a second device.

        token = "token2"
        res = self.mutate_register_fcm_token(token=token)
        assert not res["errors"]
        assert res["successMessage"] == Messages.FCM_TOKEN_UPDATED
        assert FCMDevice.objects.count() == 2
        FCMDevice.objects.get(user=user, registration_id=token)

        # Update existing token.

        token = "token2"
        res = self.mutate_register_fcm_token(token=token)
        assert not res["errors"]
        assert res["successMessage"] == Messages.FCM_TOKEN_UPDATED
        assert FCMDevice.objects.count() == 2
        FCMDevice.objects.get(user=user, registration_id=token)
