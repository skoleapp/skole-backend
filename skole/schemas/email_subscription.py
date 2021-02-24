from __future__ import annotations

from typing import Optional

import graphene
from django.core.exceptions import ObjectDoesNotExist
from django.core.signing import BadSignature
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoFormMutation, DjangoModelFormMutation

from skole.forms import CreateEmailSubscriptionForm, UpdateEmailSubscriptionForm
from skole.models import EmailSubscription
from skole.schemas.base import SkoleCreateUpdateMutationMixin, SkoleObjectType
from skole.schemas.mixins import SuccessMessageMixin
from skole.types import ResolveInfo
from skole.utils.constants import Messages, MutationErrors, TokenAction
from skole.utils.exceptions import TokenScopeError
from skole.utils.token import get_token_payload


class EmailSubscriptionObjectType(DjangoObjectType):
    class Meta:
        model = EmailSubscription
        fields = (
            "email",
            "product_updates",
            "blog_posts",
        )


class CreateEmailSubscriptionMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoFormMutation
):
    """Subscribe to marketing emails."""

    success_message_value = Messages.SUBSCRIBED

    class Meta:
        form_class = CreateEmailSubscriptionForm
        exclude_fields = ("id",)


class UpdateEmailSubscriptionMutation(
    SkoleCreateUpdateMutationMixin, DjangoModelFormMutation
):
    """Modify or delete and existing email subscription."""

    email_subscription = graphene.Field(EmailSubscriptionObjectType)
    success_message = graphene.String()

    class Meta:
        form_class = UpdateEmailSubscriptionForm
        exclude_fields = ("id",)
        return_field_name = "email_subscription"

    @classmethod
    def perform_mutate(
        cls, form: UpdateEmailSubscriptionForm, info: ResolveInfo
    ) -> UpdateEmailSubscriptionMutation:
        try:
            (
                email_subscription,
                deleted,
            ) = EmailSubscription.objects.update_email_subscription(**form.cleaned_data)
        except (ObjectDoesNotExist, BadSignature):
            return cls(errors=MutationErrors.INVALID_TOKEN)
        else:
            if deleted:
                success_message = Messages.SUBSCRIPTION_DELETED
            else:
                success_message = Messages.SUBSCRIPTION_UPDATED

            return cls(
                email_subscription=email_subscription, success_message=success_message
            )


class Query(SkoleObjectType):
    email_subscription = graphene.Field(
        EmailSubscriptionObjectType, token=graphene.String()
    )

    @staticmethod
    def resolve_email_subscription(
        root: None, info: ResolveInfo, token: str
    ) -> Optional[EmailSubscription]:
        try:
            payload = get_token_payload(
                token=token, action=TokenAction.UPDATE_EMAIL_SUBSCRIPTION
            )
        except (BadSignature, TokenScopeError):
            return None
        else:
            return EmailSubscription.objects.get_or_none(**payload)


class Mutation(SkoleObjectType):
    create_email_subscription = CreateEmailSubscriptionMutation.Field()
    update_email_subscription = UpdateEmailSubscriptionMutation.Field()
