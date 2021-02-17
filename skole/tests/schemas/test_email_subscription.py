from django.core import signing

from skole.models import EmailSubscription
from skole.tests.helpers import SkoleSchemaTestCase, get_form_error
from skole.types import ID, JsonDict
from skole.utils.constants import (
    Messages,
    MutationErrors,
    TokenAction,
    ValidationErrors,
)


class EmailSubscirptionSchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    # language=GraphQL
    email_subscription_fields = """
        fragment emailSubscriptionFields on EmailSubscriptionObjectType {
            email
            productUpdates
            blogPosts
        }
    """

    def query_email_subscription(self, *, token: str) -> JsonDict:
        variables = {"token": token}

        # language=GraphQL
        graphql = (
            self.email_subscription_fields
            + """
            query EmailSubscription($token: String!) {
                emailSubscription(token: $token) {
                    ...emailSubscriptionFields
                }
            }
            """
        )
        return self.execute(graphql, variables=variables)

    def mutate_crate_email_subscription(
        self,
        email: str,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="createEmailSubscription",
            input_type="CreateEmailSubscriptionMutationInput!",
            input={
                "email": email,
            },
            result="successMessage",
        )

    def mutate_update_email_subscription(
        self,
        token: str,
        product_updates: bool,
        blog_posts: bool,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="updateEmailSubscription",
            input_type="UpdateEmailSubscriptionMutationInput!",
            input={
                "token": token,
                "productUpdates": product_updates,
                "blogPosts": blog_posts,
            },
            result="emailSubscription { ...emailSubscriptionFields } successMessage",
            fragment=self.email_subscription_fields,
        )

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.email_subscription_fields)

    def test_create_email_subscription(self) -> None:
        # Test that it works.

        email = "test@test.com"
        res = self.mutate_crate_email_subscription(email=email)
        assert not res["errors"]
        assert res["successMessage"] == Messages.SUBSCRIBED
        assert EmailSubscription.objects.get(email=email)

        # Test that cannot create a subscription with an email that has already subscribed.

        res = self.mutate_crate_email_subscription(email=email)
        assert ValidationErrors.EMAIL_ALREADY_SUBSCRIBED == get_form_error(res)

        # Test that cannot create a subscription with an email that has a registered account.

        res = self.mutate_crate_email_subscription(email="testuser2@test.com")
        assert ValidationErrors.ACCOUNT_EMAIL == get_form_error(res)

    def test_update_email_subscription(self) -> None:
        # Test that it works.

        email = "subscriber@test.com"
        subscriber = EmailSubscription.objects.get(email=email)
        assert subscriber.product_updates
        assert not subscriber.blog_posts
        payload = {"email": email, "action": TokenAction.UPDATE_EMAIL_SUBSCRIPTION}
        token = signing.dumps(payload)
        res = self.mutate_update_email_subscription(
            token=token, product_updates=False, blog_posts=True
        )
        assert res["successMessage"] == Messages.SUBSCRIPTION_UPDATED
        assert not res["emailSubscription"]["productUpdates"]
        assert res["emailSubscription"]["blogPosts"]

        # Test with invalid token.

        res = self.mutate_update_email_subscription(
            token="invalid-token", product_updates=False, blog_posts=True
        )
        assert MutationErrors.INVALID_TOKEN == res["errors"]
        assert not res["emailSubscription"]

        # Test deleting subscription.

        res = self.mutate_update_email_subscription(
            token=token, product_updates=False, blog_posts=False
        )
        assert res["successMessage"] == Messages.SUBSCRIPTION_DELETED
        assert not res["emailSubscription"]
        assert not EmailSubscription.objects.get_or_none(email=email)
