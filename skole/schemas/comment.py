from typing import Union, cast

import graphene
from django.conf import settings
from django.db.models import Q, QuerySet
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from skole.forms import CreateCommentForm, DeleteCommentForm, UpdateCommentForm
from skole.models import Comment, Course, Resource, School, User
from skole.overridden import login_required
from skole.schemas.base import (
    SkoleCreateUpdateMutationMixin,
    SkoleDeleteMutationMixin,
    SkoleObjectType,
)
from skole.schemas.course import CourseObjectType
from skole.schemas.mixins import PaginationMixin, SuccessMessageMixin, VoteMixin
from skole.schemas.resource import ResourceObjectType
from skole.schemas.school import SchoolObjectType
from skole.types import ID, ResolveInfo
from skole.utils.constants import Messages
from skole.utils.pagination import get_paginator


class CommentObjectType(VoteMixin, DjangoObjectType):
    reply_count = graphene.Int()
    attachment_thumbnail = graphene.String()

    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "text",
            "attachment",
            "attachment_thumbnail",
            "course",
            "resource",
            "school",
            "comment",
            "reply_comments",
            "reply_count",
            "score",
            "modified",
            "created",
        )

    @staticmethod
    def resolve_attachment(root: Comment, info: ResolveInfo) -> str:
        return root.attachment.url if root.attachment else ""

    @staticmethod
    def resolve_attachment_thumbnail(root: Comment, info: ResolveInfo) -> str:
        return root.attachment_thumbnail.url if root.attachment_thumbnail else ""

    @staticmethod
    def resolve_reply_count(root: Comment, info: ResolveInfo) -> int:
        # When the Comment is created and returned from a ModelForm it will not have
        # this field computed (it gets annotated only in the model manager) since the
        # value of this would be obviously 0 at the time of the comment's creation,
        # it's ok to return it as the default here.
        return getattr(root, "reply_count", 0)


class PaginatedCommentObjectType(PaginationMixin, SkoleObjectType):
    objects = graphene.List(CommentObjectType)

    class Meta:
        description = Comment.__doc__


class CreateCommentMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """
    Create a new comment.

    Attachments are popped of for unauthenticated users. The `user` field must match
    with the ID of the user making the query to save the user making the query as the
    author of the comment. This way even authenticated users can create anonymous
    comments by setting the `user` field as `null`.
    """

    success_message_value = Messages.MESSAGE_SENT

    class Meta:
        form_class = CreateCommentForm
        exclude_fields = ("id",)  # Without this, graphene adds the field on its own.


class UpdateCommentMutation(
    SkoleCreateUpdateMutationMixin, SuccessMessageMixin, DjangoModelFormMutation
):
    """Update an existing comment."""

    login_required = True
    success_message_value = Messages.COMMENT_UPDATED
    comment = graphene.Field(CommentObjectType)

    class Meta:
        form_class = UpdateCommentForm


class DeleteCommentMutation(SkoleDeleteMutationMixin, DjangoModelFormMutation):
    """Delete a comment."""

    success_message_value = Messages.COMMENT_DELETED

    class Meta(SkoleDeleteMutationMixin.Meta):
        form_class = DeleteCommentForm


class DiscussionsUnion(graphene.Union):
    class Meta:
        types = (CourseObjectType, ResourceObjectType, SchoolObjectType)


class Query(SkoleObjectType):
    comments = graphene.Field(
        PaginatedCommentObjectType,
        user=graphene.String(),
        page=graphene.Int(),
        page_size=graphene.Int(),
    )

    discussion = graphene.List(
        CommentObjectType,
        course=graphene.ID(),
        resource=graphene.ID(),
        school=graphene.ID(),
    )

    discussion_suggestions = graphene.List(DiscussionsUnion)

    @staticmethod
    def resolve_comments(
        root: None,
        info: ResolveInfo,
        user: str = "",
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> PaginatedCommentObjectType:
        """Return comments filtered by query params."""

        qs: QuerySet[Comment] = Comment.objects.all()

        if user != "":
            qs = qs.filter(user__slug=user)

        return get_paginator(qs, page_size, page, PaginatedCommentObjectType)

    @staticmethod
    def resolve_discussion(
        root: None,
        info: ResolveInfo,
        course: ID = None,
        resource: ID = None,
        school: ID = None,
    ) -> QuerySet[Comment]:
        """Return comments filtered by query params."""

        qs = Comment.objects.all()

        if course is not None:
            qs = qs.filter(course__pk=course)
        if resource is not None:
            qs = qs.filter(resource__pk=resource)
        if school is not None:
            qs = qs.filter(school__pk=school)

        return qs

    @staticmethod
    @login_required
    def resolve_discussion_suggestions(
        root: None, info: ResolveInfo
    ) -> list[Union[School, Course, Resource]]:
        """Return a selection of courses, resources and schools that are most relevant
        to discuss for the given user."""

        user = cast(User, info.context.user)
        city = getattr(user.school, "city", None)
        country = getattr(city, "country", None)
        cut = settings.DISCUSSION_SUGGESTIONS_COUNT // 3

        # Include schools that:
        # - Is the user's school.
        # - Have been commented by the user.
        # - Have reply comments from the user.
        schools = (
            School.objects.filter(
                Q(users=user)
                | Q(comments__user=user)
                | Q(comments__reply_comments__user=user)
            )
            .order_by("-comment_count")
            .distinct()
        )

        # If there are not enough schools in the queryset, add the best schools from the user's city.
        if len(schools) < cut:
            schools = schools.union(
                School.objects.filter(city=city).order_by("-comment_count")
            ).distinct()

        # If there are still not enough schools, do the same based on the user's country.
        if len(schools) < cut:
            schools = schools.union(
                School.objects.filter(city__country=country).order_by("-comment_count")
            ).distinct()

        # Include courses that:
        # - Are created by the user.
        # - Have been starred by the user.
        # - Have been voted by the user.
        # - Have been commented by the user.
        # - Have reply comments from the user.
        # - Have resources added by the user.
        courses = (
            Course.objects.filter(
                Q(user=user)
                | Q(stars__user=user)
                | Q(votes__user=user)
                | Q(comments__user=user)
                | Q(comments__reply_comments__user=user)
                | Q(resources__user=user)
            )
            .order_by("-score", "-resource_count", "-comment_count")
            .distinct()
        )

        # If there are not enough courses in the queryset, add the best courses from the user's subject.
        if len(courses) < cut:
            courses = courses.union(
                Course.objects.filter(subjects=user.subject).order_by(
                    "-score", "-resource_count", "-comment_count"
                )
            ).distinct()

        # Include resources that:
        # - Are created by the user.
        # - Have their course created by the user.
        # - Have been starred by the user.
        # - Have been voted by the user.
        # - Have been commented by the user.
        # - Have reply comments from the user.
        resources = (
            Resource.objects.filter(
                Q(user=user)
                | Q(course__user=user)
                | Q(stars__user=user)
                | Q(votes__user=user)
                | Q(comments__user=user)
                | Q(comments__reply_comments__user=user)
            )
            .order_by("-score", "-comment_count")
            .distinct()
        )

        # If there are not enough resources in the queryset, add the best resources from the user's subject.
        if len(resources) < cut:
            resources = resources.union(
                Resource.objects.filter(course__subjects=user.subject).order_by(
                    "-score", "-comment_count"
                )
            ).distinct()

        return [*schools[:cut], *courses[:cut], *resources[:cut]]


class Mutation(SkoleObjectType):
    create_comment = CreateCommentMutation.Field()
    update_comment = UpdateCommentMutation.Field()
    delete_comment = DeleteCommentMutation.Field()
