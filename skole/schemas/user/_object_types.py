from functools import wraps
from typing import Callable, Optional, TypeVar

import graphene
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from fcm_django.models import FCMDevice

from skole.models import Badge, BadgeProgress, School, Subject, User
from skole.schemas.badge import BadgeObjectType
from skole.schemas.badge_progress import BadgeProgressObjectType
from skole.schemas.base import SkoleDjangoObjectType
from skole.schemas.school import SchoolObjectType
from skole.schemas.subject import SubjectObjectType
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
    querying one's own profile: `email`, `verified`, `badge_progresses`,
    `selected_badge_progress` `school`, `subject`, and all `permission` fields.

    For instances that are not the user's own user profile, these fields will return a
    `null` value.
    """

    slug = graphene.String()
    email = graphene.String()
    score = graphene.Int()
    avatar = graphene.String()
    avatar_thumbnail = graphene.String()
    verified = graphene.Boolean()
    school = graphene.Field(SchoolObjectType)
    subject = graphene.Field(SubjectObjectType)
    rank = graphene.String()
    badges = graphene.List(BadgeObjectType)
    badge_progresses = graphene.List(BadgeProgressObjectType)
    unread_activity_count = graphene.Int()
    fcm_token = graphene.String()
    product_update_email_permission = graphene.Boolean()
    blog_post_email_permission = graphene.Boolean()
    comment_reply_email_permission = graphene.Boolean()
    course_comment_email_permission = graphene.Boolean()
    resource_comment_email_permission = graphene.Boolean()
    comment_reply_push_permission = graphene.Boolean()
    course_comment_push_permission = graphene.Boolean()
    resource_comment_push_permission = graphene.Boolean()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "slug",
            "username",
            "email",
            "score",
            "title",
            "bio",
            "avatar",
            "avatar_thumbnail",
            "created",
            "verified",
            "selected_badge_progress",
            "unread_activity_count",
            "fcm_token",
            "product_update_email_permission",
            "blog_post_email_permission",
            "comment_reply_email_permission",
            "course_comment_email_permission",
            "resource_comment_email_permission",
            "comment_reply_push_permission",
            "course_comment_push_permission",
            "resource_comment_push_permission",
        )

    @staticmethod
    def resolve_avatar(root: User, info: ResolveInfo) -> str:
        return root.avatar.url if root.avatar else ""

    @staticmethod
    def resolve_avatar_thumbnail(root: User, info: ResolveInfo) -> str:
        return root.avatar_thumbnail.url if root.avatar_thumbnail else ""

    @staticmethod
    def resolve_badges(root: User, info: ResolveInfo) -> QuerySet[Badge]:
        return Badge.objects.filter(
            badge_progresses__user=root, badge_progresses__acquired__isnull=False
        )

    @staticmethod
    @private_field
    def resolve_badge_progresses(
        root: User, info: ResolveInfo
    ) -> QuerySet[BadgeProgress]:
        return root.get_or_create_badge_progresses()

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
    def resolve_verified(root: User, info: ResolveInfo) -> bool:
        return root.verified

    @staticmethod
    @private_field
    def resolve_school(root: User, info: ResolveInfo) -> Optional[School]:
        return root.school

    @staticmethod
    @private_field
    def resolve_subject(root: User, info: ResolveInfo) -> Optional[Subject]:
        return root.subject

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
    def resolve_product_update_email_permission(root: User, info: ResolveInfo) -> bool:
        return root.product_update_email_permission

    @staticmethod
    @private_field
    def resolve_blog_post_email_permission(root: User, info: ResolveInfo) -> bool:
        return root.blog_post_email_permission

    @staticmethod
    @private_field
    def resolve_comment_reply_email_permission(root: User, info: ResolveInfo) -> bool:
        return root.comment_reply_email_permission

    @staticmethod
    @private_field
    def resolve_course_comment_email_permission(root: User, info: ResolveInfo) -> bool:
        return root.course_comment_email_permission

    @staticmethod
    @private_field
    def resolve_resource_comment_email_permission(
        root: User, info: ResolveInfo
    ) -> bool:
        return root.resource_comment_email_permission

    @staticmethod
    @private_field
    def resolve_comment_reply_push_permission(root: User, info: ResolveInfo) -> bool:
        return root.comment_reply_push_permission

    @staticmethod
    @private_field
    def resolve_course_comment_push_permission(root: User, info: ResolveInfo) -> bool:
        return root.course_comment_push_permission

    @staticmethod
    @private_field
    def resolve_resource_comment_push_permission(root: User, info: ResolveInfo) -> bool:
        return root.resource_comment_push_permission
