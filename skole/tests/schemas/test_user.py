# pylint: disable=too-many-lines
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
from skole.tests.schemas.test_badge import BadgeSchemaTests
from skole.types import ID, JsonDict
from skole.utils.constants import Errors, Messages, MutationErrors

# language=GraphQL
badge_progress_fields = (
    BadgeSchemaTests.badge_fields
    + """
    fragment badgeProgressFields on BadgeProgressObjectType {
        badge {
            ...badgeFields
        }
        progress
        steps
    }
    """
)


class UserSchemaTests(SkoleSchemaTestCase):  # pylint: disable=too-many-public-methods
    authenticated_user: ID = 2

    # language=GraphQL
    user_fields = (
        badge_progress_fields
        + """
        fragment userFields on UserObjectType {
            id
            slug
            username
            email
            backupEmail
            title
            bio
            avatar
            avatarThumbnail
            score
            rank
            verified
            unreadActivityCount
            threadCount
            commentCount
            created
            modified
            fcmToken
            commentReplyEmailPermission
            threadCommentEmailPermission
            newBadgeEmailPermission
            commentReplyPushPermission
            threadCommentPushPermission
            newBadgePushPermission
            badges {
                ...badgeFields
            }
            badgeProgresses {
                ...badgeProgressFields
            }
            selectedBadgeProgress {
                ...badgeProgressFields
            }
            referralCodes {
                code
                usages
            }
        }
        """
    )

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
        email: str = "newemail@test.test",
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
        title: str = "",
        bio: str = "",
        avatar: str = "uploads/avatars/test_avatar.jpg",
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
        email: str = "testuser2@test.test",
        backup_email: str = "",
        comment_reply_email_permission: bool = False,
        thread_comment_email_permission: bool = False,
        new_badge_email_permission: bool = False,
        comment_reply_push_permission: bool = True,
        thread_comment_push_permission: bool = True,
        new_badge_push_permission: bool = True,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="updateAccountSettings",
            input_type="UpdateAccountSettingsMutationInput!",
            input={
                "email": email,
                "backupEmail": backup_email,
                "commentReplyEmailPermission": comment_reply_email_permission,
                "threadCommentEmailPermission": thread_comment_email_permission,
                "newBadgeEmailPermission": new_badge_email_permission,
                "commentReplyPushPermission": comment_reply_push_permission,
                "threadCommentPushPermission": thread_comment_push_permission,
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
        self, *, email: str = "testuser2@test.test"
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

    def mutate_verify_backup_email(self, *, token: str) -> JsonDict:
        return self.execute_input_mutation(
            name="verifyBackupEmail",
            input_type="VerifyBackupEmailMutationInput!",
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

    def mutate_resend_backup_email_verification_email(
        self, assert_error: bool = False
    ) -> JsonDict:
        return self.execute_non_input_mutation(
            name="resendBackupEmailVerificationEmail",
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

        email = "newemail@test.test"
        res = self.mutate_register(email=email)
        assert not res["errors"]
        assert res["successMessage"] == Messages.USER_REGISTERED
        get_user_model().objects.order_by("created")

        res = self.mutate_register(username="unique", email="unique@test.test")
        assert not res["errors"]
        get_user_model().objects.order_by("created")

        # Username should keep its casing, mut email should be lowercased.
        self.mutate_register(username="MYUSERNAME", email="MAIL@test.TEST")
        user = get_last(get_user_model().objects.order_by("created"))
        assert user.username == "MYUSERNAME"
        assert user.email == "mail@test.test"

        # No verification email are sent before referral codes are used.
        assert len(mail.outbox) == 0

    def test_register_error(self) -> None:
        self.authenticated_user = None

        # Username taken.
        res = self.mutate_register(username="testuser2")
        assert Errors.USERNAME_TAKEN == get_form_error(res)

        # Username taken with different casing.
        res = self.mutate_register(username="TESTUSER2")
        assert Errors.USERNAME_TAKEN == get_form_error(res)

        # Invalid characters in username.
        res = self.mutate_register(username="@testuser")
        assert Errors.INVALID_USERNAME == get_form_error(res)

        # Email taken.
        res = self.mutate_register(email="testuser2@test.test")
        assert Errors.EMAIL_TAKEN == get_form_error(res)

        # Email taken with different casing.
        res = self.mutate_register(email="TESTUSER2@test.test")
        assert Errors.EMAIL_TAKEN == get_form_error(res)

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

        # Non allowed email domain.
        res = self.mutate_register(email="email@nonallowed.test")
        assert get_form_error(res) == Errors.EMAIL_DOMAIN_NOT_ALLOWED

    def test_use_referral_code_ok(self) -> None:
        email = "newemail@test.test"
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
        email = "newemail@test.test"
        self.mutate_register(email=email)

        # Invalid referral code.
        res = self.mutate_use_referral_code(code="INVALID", email=email)
        assert get_form_error(res) == Errors.REFERRAL_CODE_INVALID

        # No account for the email.
        res = self.mutate_use_referral_code(code="TEST1", email="invalid@test.test")
        assert get_form_error(res) == Errors.EMAIL_DOES_NOT_EXIST

        assert len(mail.outbox) == 0  # No verification emails sent.

    def test_verify_ok(self) -> None:
        email = "newemail@test.test"
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
        assert get_graphql_error(res) == Errors.AUTH_REQUIRED

    def test_resend_verification_email(self) -> None:
        self.authenticated_user = 3  # Not yet verified.
        res = self.mutate_resend_verification_email()
        assert not res["errors"]

        assert len(mail.outbox) == 1
        sent = mail.outbox[0]
        assert sent.from_email == settings.EMAIL_ADDRESS
        assert sent.to == ["testuser3@test.test"]
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

    def test_verify_backup_email(self) -> None:
        self.mutate_update_account_settings(backup_email="newbackup@test.test")
        assert len(mail.outbox) == 1
        token = get_token_from_email(mail.outbox[0].body)
        res = self.mutate_verify_backup_email(token=token)
        assert not res["errors"]
        assert res["successMessage"] == Messages.BACKUP_EMAIL_VERIFIED

        res = self.mutate_verify_backup_email(token=token)
        assert res["errors"] == MutationErrors.BACKUP_EMAIL_ALREADY_VERIFIED

    def test_resend_backup_email_verification_email(self) -> None:
        user = self.get_authenticated_user()
        user.backup_email = "backup@test.test"
        user.verified_backup_email = False
        user.save()

        self.mutate_resend_backup_email_verification_email()
        self.mutate_resend_backup_email_verification_email()
        self.mutate_resend_backup_email_verification_email()
        assert len(mail.outbox) == 3
        res = self.mutate_verify_backup_email(
            token=get_token_from_email(mail.outbox[0].body)
        )
        assert not res["errors"]
        assert res["successMessage"] == Messages.BACKUP_EMAIL_VERIFIED

    def test_login_ok_with_username(self) -> None:
        self.authenticated_user = None

        res = self.mutate_login()
        assert res["user"]["email"] == "testuser2@test.test"
        assert res["user"]["username"] == "testuser2"
        assert res["successMessage"] == Messages.LOGGED_IN

        # Username is not case sensitive on login.
        res = self.mutate_login(username_or_email="TestUSER2")
        assert res["user"]["email"] == "testuser2@test.test"
        assert res["user"]["username"] == "testuser2"
        assert res["successMessage"] == Messages.LOGGED_IN

    def test_login_ok_with_email(self) -> None:
        self.authenticated_user = None

        res = self.mutate_login(username_or_email="testuser2@test.test")
        assert res["user"]["email"] == "testuser2@test.test"
        assert res["user"]["username"] == "testuser2"
        assert res["successMessage"] == Messages.LOGGED_IN

        # Email is not case sensitive on login.
        res = self.mutate_login(username_or_email="TESTUSER2@test.TEST")
        assert res["user"]["email"] == "testuser2@test.test"
        assert res["user"]["username"] == "testuser2"
        assert res["successMessage"] == Messages.LOGGED_IN

    def test_login_ok_with_backup_email(self) -> None:
        backup_email = "backup@test.test"
        user = self.get_authenticated_user()
        user.backup_email = backup_email
        user.save()

        self.authenticated_user = None
        res = self.mutate_login(username_or_email=backup_email)
        assert not res["errors"]
        assert res["user"]["username"] == "testuser2"
        assert res["user"]["backupEmail"] == backup_email
        assert res["successMessage"] == Messages.LOGGED_IN

    def test_login_error(self) -> None:
        self.authenticated_user = None

        # Invalid username.
        res = self.mutate_login(username_or_email="badusername")
        assert get_form_error(res) == Errors.AUTH_ERROR

        # Invalid email.
        res = self.mutate_login(username_or_email="bademail@test.test")
        assert get_form_error(res) == Errors.AUTH_ERROR

        # Invalid password.
        res = self.mutate_login(password="wrongpass")
        assert get_form_error(res) == Errors.AUTH_ERROR

    def test_register_and_login(self) -> None:
        self.authenticated_user = None

        username = "newuser2"
        email = "newemail2@test.test"
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
        assert user1["email"] == "testuser2@test.test"
        assert user1["verified"]
        assert user1["rank"] == "Freshman"
        assert user1["threadCount"] == 3
        assert user1["commentCount"] == 14
        assert user1["unreadActivityCount"] == 3
        assert user1["fcmToken"] is None
        assert len(user1["badges"]) == 1
        assert len(user1["badgeProgresses"]) == 4
        assert user1["badgeProgresses"][0]["badge"]["id"] == "3"
        assert user1["badgeProgresses"][0]["badge"]["name"] == "First Comment"
        assert user1["badgeProgresses"][0]["progress"] == 0
        assert user1["badgeProgresses"][0]["steps"] == 1
        assert user1["selectedBadgeProgress"]["badge"]["id"] == "3"
        assert user1["selectedBadgeProgress"]["badge"]["name"] == "First Comment"
        assert user1["selectedBadgeProgress"]["progress"] == 0
        assert user1["selectedBadgeProgress"]["steps"] == 1
        assert len(user1["referralCodes"]) == 1
        assert user1["referralCodes"][0]["code"] == "TEST1"
        assert user1["referralCodes"][0]["usages"] == 2

        # Some other user.
        slug = "testuser3"
        user2 = self.query_user(slug=slug)
        assert user2["id"] == "3"
        assert user2["username"] == "testuser3"
        assert user2["slug"] == slug
        assert user2["rank"] == "Tutor"
        assert user2["threadCount"] == 4
        assert user2["commentCount"] == 3
        assert len(user2["badges"]) == 0

        # Private fields.
        assert user2["badgeProgresses"] is None
        assert user2["selectedBadgeProgress"] is None
        assert user2["referralCodes"] is None
        assert user2["unreadActivityCount"] is None
        assert user2["fcmToken"] is None
        assert user2["email"] is None
        assert user2["verified"] is None

        # Slug not found.
        assert self.query_user(slug="not-found") is None

    def test_user_me(self) -> None:
        user = self.query_user_me()
        assert user["id"] == "2"
        assert user["username"] == "testuser2"
        assert user["slug"] == "testuser2"
        assert user["email"] == "testuser2@test.test"
        assert user["verified"]
        assert user["rank"] == "Freshman"
        assert user["threadCount"] == 3
        assert user["commentCount"] == 14
        assert user["unreadActivityCount"] == 3
        assert user["fcmToken"] is None
        assert len(user["badges"]) == 1
        assert user["badges"][0]["name"] == "Staff"
        assert len(user["badgeProgresses"]) == 4

        # `badgeProgresses` should be sorted by their completion percentage.
        assert user["badgeProgresses"][0]["badge"]["name"] == "First Comment"
        badge_progress = BadgeProgress.objects.get(badge__identifier="first_upvote")
        badge_progress.badge.steps = 10
        badge_progress.progress = 9
        badge_progress.save()
        user = self.query_user_me()
        assert user["badgeProgresses"][0]["badge"]["name"] == "First Upvote"
        assert user["badgeProgresses"][1]["badge"]["name"] == "First Comment"

        assert len(user["referralCodes"]) == 1
        assert user["referralCodes"][0]["code"] == "TEST1"
        assert user["referralCodes"][0]["usages"] == 2

        # Shouldn't work without auth.
        self.authenticated_user = None
        res = self.query_user_me(assert_error=True)
        assert get_graphql_error(res) == Errors.AUTH_REQUIRED
        assert res["data"] == {"userMe": None}

    def test_update_profile(self) -> None:
        # Fine to not change anything.
        user = self.query_user_me()
        res = self.mutate_update_profile()
        assert not res["errors"]

        for key, value in res["user"].items():
            if key != "modified":
                assert value == user[key]

        assert res["successMessage"] == Messages.PROFILE_UPDATED

        # Fine to change the casing of the username.
        current_user = self.get_authenticated_user()
        res = self.mutate_update_profile(username=current_user.username.upper())
        assert not res["errors"]
        assert res["user"]["username"] == "TESTUSER2"

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
        assert get_form_error(res) == Errors.USERNAME_TAKEN
        assert res["user"] is None

        # Invalid characters in username.
        res = self.mutate_update_profile(username="test-user")
        assert Errors.INVALID_USERNAME == get_form_error(res)

        # Same username with different casing is already taken.
        res = self.mutate_update_profile(username="TESTUSER3")
        assert len(res["errors"]) == 1
        assert get_form_error(res) == Errors.USERNAME_TAKEN
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

    def test_update_account_settings(  # pylint: disable=too-many-statements
        self,
    ) -> None:
        # Fine to not change anything.
        user = self.query_user_me()
        res = self.mutate_update_account_settings()
        assert not res["errors"]

        for key, value in res["user"].items():
            if key != "modified":
                assert value == user[key]

        assert res["successMessage"] == Messages.ACCOUNT_SETTINGS_UPDATED

        # User is currently verified.
        current_user = self.get_authenticated_user()
        assert current_user.verified

        # Changing the email to the current one with different casing shouldn't do anything.
        res = self.mutate_update_account_settings(email=current_user.email.upper())
        assert not res["errors"]
        current_user.refresh_from_db()
        assert current_user.verified
        assert current_user.email == "testuser2@test.test"

        # Update some fields.
        comment_reply_email_permission = True
        thread_comment_email_permission = True
        new_badge_email_permission = True
        comment_reply_push_permission = True
        thread_comment_push_permission = True
        new_badge_push_permission = True

        res = self.mutate_update_account_settings(
            comment_reply_email_permission=comment_reply_email_permission,
            thread_comment_email_permission=thread_comment_email_permission,
            new_badge_email_permission=new_badge_email_permission,
            comment_reply_push_permission=comment_reply_push_permission,
            thread_comment_push_permission=thread_comment_push_permission,
            new_badge_push_permission=new_badge_push_permission,
        )
        assert not res["errors"]
        assert res["user"]["commentReplyEmailPermission"]
        assert res["user"]["threadCommentEmailPermission"]
        assert res["user"]["newBadgeEmailPermission"]
        assert res["user"]["commentReplyPushPermission"]
        assert res["user"]["threadCommentPushPermission"]
        assert res["user"]["newBadgePushPermission"]
        assert res["successMessage"] == Messages.ACCOUNT_SETTINGS_UPDATED

        # Changing the backup email should unverify it and send a verification email.
        assert len(mail.outbox) == 0
        current_user.verified_backup_email = True
        current_user.save()
        new_backup_email = "newbackup@test.test"
        res = self.mutate_update_account_settings(backup_email=new_backup_email)
        assert not res["errors"]
        assert res["user"]["backupEmail"] == new_backup_email
        current_user.refresh_from_db()
        assert len(mail.outbox) == 1
        assert current_user.verified
        assert not current_user.verified_backup_email
        assert current_user.backup_email == new_backup_email

        # Changing the email should unverify the user and send a verification email.
        new_mail = "newmail@test.test"
        res = self.mutate_update_account_settings(email="NEWMAIL@test.test")
        assert not res["errors"]
        assert res["user"]["email"] == new_mail
        current_user.refresh_from_db()
        assert not current_user.verified
        assert current_user.email == new_mail
        assert len(mail.outbox) == 2

        user_old = self.query_user_me()

        # Email is already taken.
        res = self.mutate_update_account_settings(email="admin@test.test")
        assert len(res["errors"]) == 1
        assert get_form_error(res) == Errors.EMAIL_TAKEN
        assert res["user"] is None

        # Same email with different casing is already taken.
        res = self.mutate_update_account_settings(email="ADMIN@test.test")
        assert len(res["errors"]) == 1
        assert get_form_error(res) == Errors.EMAIL_TAKEN
        assert res["user"] is None

        # Non allowed email domain.
        res = self.mutate_update_account_settings(email="email@nonallowed.test")
        assert get_form_error(res) == Errors.EMAIL_DOMAIN_NOT_ALLOWED

        # Backup email cannot be the email of another user.
        res = self.mutate_update_account_settings(backup_email="testuser3@test.test")
        assert get_form_error(res) == Errors.EMAIL_TAKEN

        # Backup email cannot be the same as primary email.
        res = self.mutate_update_account_settings(
            email=current_user.email, backup_email=current_user.email
        )
        assert get_form_error(res) == Errors.BACKUP_EMAIL_NOT_SAME_AS_EMAIL

        # Check that nothing has changed.
        assert self.query_user_me() == user_old

    def test_delete_user(self) -> None:
        old_count = get_user_model().objects.count()

        # Test deleting user with wrong password.
        res = self.mutate_delete_user(password="wrongpass")
        assert get_form_error(res) == Errors.INVALID_PASSWORD

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
        assert get_form_error(res) == Errors.INVALID_OLD_PASSWORD

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
        res = self.mutate_change_password(new_password="testuser2@test.test")
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
        email = "testuser2@test.test"
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
        email = "TESTUSER2@TEST.test"
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
        res = self.mutate_send_password_reset_email(email="foobar@test.test")
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
        res = self.mutate_reset_password(
            token=token, new_password="testuser2@test.test"
        )
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
