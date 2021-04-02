from functools import wraps
from typing import Callable, Optional, TypeVar

import graphene
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from fcm_django.models import FCMDevice

from skole.models import Badge, BadgeProgress, ReferralCode, User
from skole.schemas.badge import BadgeObjectType
from skole.schemas.badge_progress import BadgeProgressObjectType
from skole.schemas.base import SkoleDjangoObjectType
from skole.schemas.referral_code import ReferralCodeObjectType
from skole.types import ResolveInfo

T = TypeVar("T")
UserResolver = Callable[[User, ResolveInfo], T]


def private_field(func: UserResolver[T]) -> UserResolver[Optional[T]]:
    """Use as a decorator to only return the field's value if it's the user's own."""

    @wraps(func)
    def wrapper(root: User, info: ResolveInfo) -> Optional[T]:
        if info.context.user.is_authenticated and root.pk == info.context.user.pk:
            return func(root, info)
        else:
            return None

    return wrapper


class UserObjectType(SkoleDjangoObjectType):
    """
    The following fields are private, meaning they are returned only if the user is
    querying one's own profile: `email`, `backup_email`, `verified`, `badge_progresses`,
    `selected_badge_progress`, `referral_codes`, and all `permission` fields.

    For instances that are not the user's own user profile, these fields will return a
    `null` value.
    """

    email = graphene.String()
    backup_email = graphene.String()
    thread_count = graphene.Int()
    comment_count = graphene.Int()
    avatar_thumbnail = graphene.String()
    verified = graphene.Boolean()
    rank = graphene.String()
    badges = graphene.List(BadgeObjectType)
    badge_progresses = graphene.List(BadgeProgressObjectType)
    referral_codes = graphene.List(ReferralCodeObjectType)
    unread_activity_count = graphene.Int()
    fcm_token = graphene.String()
    comment_reply_email_permission = graphene.Boolean()
    thread_comment_email_permission = graphene.Boolean()
    new_badge_email_permission = graphene.Boolean()
    comment_reply_push_permission = graphene.Boolean()
    thread_comment_push_permission = graphene.Boolean()
    new_badge_push_permission = graphene.Boolean()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "slug",
            "username",
            "email",
            "backup_email",
            "title",
            "bio",
            "avatar",
            "avatar_thumbnail",
            "score",
            "rank",
            "thread_count",
            "comment_count",
            "verified",
            "unread_activity_count",
            "created",
            "modified",
            "fcm_token",
            "comment_reply_email_permission",
            "thread_comment_email_permission",
            "new_badge_email_permission",
            "comment_reply_push_permission",
            "thread_comment_push_permission",
            "new_badge_push_permission",
            "badges",
            "badge_progresses",
            "selected_badge_progress",
            "referral_codes",
        )

    @staticmethod
    def resolve_thread_count(root: User, info: ResolveInfo) -> int:
        return getattr(root, "thread_count", 0)

    @staticmethod
    def resolve_comment_count(root: User, info: ResolveInfo) -> int:
        return getattr(root, "comment_count", 0)

    @staticmethod
    def resolve_avatar(root: User, info: ResolveInfo) -> str:
        return root.avatar.url if root.avatar else ""

    @staticmethod
    def resolve_avatar_thumbnail(root: User, info: ResolveInfo) -> str:
        return root.avatar_thumbnail.url if root.avatar_thumbnail else ""

    @staticmethod
    def resolve_badges(root: User, info: ResolveInfo) -> QuerySet[Badge]:
        return root.get_acquired_badges()

    @staticmethod
    @private_field
    def resolve_badge_progresses(
        root: User, info: ResolveInfo
    ) -> QuerySet[BadgeProgress]:
        return root.get_or_create_badge_progresses()

    @staticmethod
    @private_field
    def resolve_referral_codes(root: User, info: ResolveInfo) -> QuerySet[ReferralCode]:
        return root.referral_codes.all()

    @staticmethod
    @private_field
    def resolve_selected_badge_progress(
        root: User, info: ResolveInfo
    ) -> Optional[BadgeProgress]:
        if root.selected_badge_progress and not root.selected_badge_progress.acquired:
            return root.selected_badge_progress
        return root.get_or_create_badge_progresses().first()

    @staticmethod
    @private_field
    def resolve_email(root: User, info: ResolveInfo) -> str:
        return root.email

    @staticmethod
    @private_field
    def resolve_backup_email(root: User, info: ResolveInfo) -> str:
        return root.backup_email

    @staticmethod
    @private_field
    def resolve_verified(root: User, info: ResolveInfo) -> bool:
        return root.verified

    @staticmethod
    @private_field
    def resolve_unread_activity_count(root: User, info: ResolveInfo) -> int:
        return root.activities.filter(read=False).order_by().count()

    @staticmethod
    @private_field
    def resolve_fcm_token(root: User, info: ResolveInfo) -> Optional[str]:
        try:
            return FCMDevice.objects.get(user=info.context.user).registration_id
        except FCMDevice.DoesNotExist:
            return None

    @staticmethod
    @private_field
    def resolve_comment_reply_email_permission(root: User, info: ResolveInfo) -> bool:
        return root.comment_reply_email_permission

    @staticmethod
    @private_field
    def resolve_thread_comment_email_permission(root: User, info: ResolveInfo) -> bool:
        return root.thread_comment_email_permission

    @staticmethod
    @private_field
    def resolve_new_badge_email_permission(root: User, info: ResolveInfo) -> bool:
        return root.new_badge_email_permission

    @staticmethod
    @private_field
    def resolve_comment_reply_push_permission(root: User, info: ResolveInfo) -> bool:
        return root.comment_reply_push_permission

    @staticmethod
    @private_field
    def resolve_thread_comment_push_permission(root: User, info: ResolveInfo) -> bool:
        return root.thread_comment_push_permission

    @staticmethod
    @private_field
    def resolve_new_badge_push_permission(root: User, info: ResolveInfo) -> bool:
        return root.new_badge_push_permission
