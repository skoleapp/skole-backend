from __future__ import annotations

import io
import itertools
import json
import math
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Any, Set, cast

import graphene
from django.conf import settings
from django.contrib.postgres.aggregates.general import ArrayAgg
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Case, CharField, F, QuerySet, Value, When
from django.db.models.fields.files import FieldFile
from django.db.models.functions import Concat, Replace
from django.template.loader import render_to_string
from django.utils import timezone, translation
from django.utils.html import strip_tags
from graphene_django.types import ErrorType

from skole.models import Activity, Badge, Comment, Course, Resource, Star, User, Vote
from skole.overridden import login_required
from skole.schemas.base import SkoleObjectType
from skole.types import ResolveInfo
from skole.utils.constants import Email, Messages, MutationErrors, VoteConstants
from skole.utils.shortcuts import format_form_error


class DjangoQuerySetJsonEncoder(DjangoJSONEncoder):
    """Json encoder which can serialize QuerySets."""

    def default(self, o: Any) -> Any:
        if isinstance(o, QuerySet):
            return list(o)
        else:
            return super().default(o)


class JSONString(graphene.JSONString):
    """A graphene JSON field which handles serializing datetimes, QuerySets and more."""

    @staticmethod
    def serialize(dt: Any) -> str:
        return json.dumps(dt, cls=DjangoQuerySetJsonEncoder)


class MyDataMutation(SkoleObjectType, graphene.Mutation):
    """Email the current user with a zip file containing **all** of their data."""

    # Can't inherit `SkoleCreateUpdateMutationMixin` since this doesn't use a form.

    # Can't use `SuccessMessageMixin` since it only works with `BaseDjangoFormMutation`.
    success_message = graphene.String()

    errors = graphene.List(ErrorType, default_value=[])

    @classmethod
    @login_required
    def mutate(cls, root: None, info: ResolveInfo) -> MyDataMutation:
        user = cast(User, info.context.user)
        if remaining := cls.__time_until_can_request_again(user):
            return cls(errors=format_form_error(MutationErrors.RATE_LIMITED, remaining))

        with translation.override(settings.LANGUAGE_CODE):
            # Everything in EN for consistency.
            data = {
                # Model fields
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "title": user.title,
                "bio": user.bio,
                "avatar": Path(user.avatar.name).name if user.avatar else None,
                "school": user.school.name if user.school else None,
                "subject": user.subject.name if user.subject else None,
                "score": user.score,
                "verified": user.verified,
                "is_active": user.is_active,
                "last_login": user.last_login,
                "modified": user.created,
                "created": user.modified,
                "last_my_data_query": user.last_my_data_query,
                # Related models
                "created_comments": cls._created_comments(user),
                "created_courses": cls._created_courses(user),
                "created_resources": cls._created_resources(user),
                "badges": cls._badges(user),
                "votes": cls._votes(user),
                "stars": cls._stars(user),
                "activities": cls._activities(user),
                "caused_activities": cls._caused_activities(user),
            }
        json_data = json.dumps(data, indent=4, cls=DjangoQuerySetJsonEncoder)
        cls.__send_email(user, json_data)
        return cls(success_message=Messages.DATA_REQUEST_RECEIVED)

    # fmt: off
    # black slaughters the formatting of long queries.
    @classmethod
    def _created_comments(cls, user: User) -> QuerySet[Comment]:
        return user.comments.annotate(
            target=cls.__target_case()
        ).annotate(
            uploaded_attachment=cls.__file_case("attachment")
        ).values(
            "id",
            "text",
            "target",
            "uploaded_attachment",
            "modified",
            "created",
        )

    @classmethod
    def _created_courses(cls, user: User) -> QuerySet[Course]:
        return user.created_courses.filter(
            subjects__translations__language_code=settings.LANGUAGE_CODE
        ).annotate(
            subject_names=ArrayAgg("subjects__translations__name", distinct=True)
        ).values(
            "id",
            "name",
            "code",
            "subject_names",
            "modified",
            "created",
        )

    @classmethod
    def _created_resources(cls, user: User) -> QuerySet[Resource]:
        return user.created_resources.filter(
            resource_type__translations__language_code=settings.LANGUAGE_CODE
        ).annotate(
            uploaded_file=cls.__file_case("file")
        ).values(
            "id",
            "course",
            "title",
            "uploaded_file",
            "modified",
            "created",
            type=F("resource_type__translations__name"),
        )
    # fmt: on

    @classmethod
    def _activities(cls, user: User) -> QuerySet[Activity]:
        return user.activities.annotate(target=cls.__target_case()).values(
            "id",
            "read",
            "target",
            type=cls.__activity_type_name(),
        )

    @classmethod
    def _caused_activities(cls, user: User) -> QuerySet[Activity]:
        return user.target_activities.annotate(target=cls.__target_case()).values(
            "id", "read", "target", type=cls.__activity_type_name()
        )

    @classmethod
    def _votes(cls, user: User) -> QuerySet[Vote]:
        return user.votes.annotate(
            target=cls.__target_case(),
            vote=Case(
                *(
                    When(status=value, then=Value(display))
                    for value, display in VoteConstants.STATUS
                ),
                output_field=CharField(),
            ),
        ).values("id", "vote", "target")

    @classmethod
    def _stars(cls, user: User) -> QuerySet[Star]:
        return user.stars.annotate(
            target=Case(
                *cls.__target_case().cases[1:]
            )  # Star doesn't have a `comment` field.
        ).values_list("target", flat=True)

    @staticmethod
    def _badges(user: User) -> QuerySet[Badge]:
        return user.badges.translated().values_list("translations__name", flat=True)

    @staticmethod
    def _uploaded_files(user: User) -> Set[FieldFile]:
        # Objects basically shouldn't have duplicate files, but our test data
        # at least has those, so better to filter them away with a `set`.
        return {
            file
            for file in itertools.chain(
                (resource.file for resource in user.created_resources.all()),
                (comment.attachment for comment in user.comments.all()),
                (user.avatar,),
            )
            if file
        }

    @classmethod
    def __send_email(cls, user: User, json_data: str) -> None:
        html_message = render_to_string(
            settings.EMAIL_TEMPLATE_MY_DATA, context={"user": user}
        )
        mail = EmailMultiAlternatives(
            subject=Email.MY_DATA_SUBJECT,
            body=strip_tags(html_message),
            from_email=settings.EMAIL_NO_REPLY,
            to=(user.email,),
            connection=get_connection(),
        )
        mail.attach_alternative(html_message, "text/html")

        assert user.last_my_data_query is not None  # Cannot be `None` anymore.

        file = Path(
            f"{user.username}_data_{user.last_my_data_query.strftime('%Y%m%d')}.zip"
        )

        buffer = io.BytesIO()

        with zipfile.ZipFile(buffer, "w") as f:
            for uploaded in cls._uploaded_files(user):
                f.writestr(f"{file.stem}/{uploaded.name}", uploaded.read())

            f.writestr(f"{file.stem}/data.json", json_data)

        content = buffer.getvalue()
        mail.attach(filename=file.name, content=content, mimetype="application/zip")

        if settings.DEBUG:
            # Write the file to disk so that it can be easily inspected in dev env.
            with open(Path(settings.MEDIA_ROOT) / file.name, "wb") as debug_f:
                debug_f.write(content)

        mail.send()

    @staticmethod
    def __time_until_can_request_again(user: User) -> int:
        # We could use something like django-ratelimit for this, but that would require
        # us to setup a cross process cache solution (like memcached) and it just feels
        # such an overkill for a simple tasks like this.
        if last_queried := user.last_my_data_query:
            now = timezone.now()
            if last_queried > now - settings.MY_DATA_RATE_LIMIT:
                remaining = settings.MY_DATA_RATE_LIMIT - (now - last_queried)
                remaining_time_in_minutes = math.ceil(remaining.total_seconds() / 60)
                return remaining_time_in_minutes
        user.update_last_my_data_query()
        return 0

    @staticmethod
    @lru_cache
    def __target_case() -> Case:
        # Critical that `comment` is the first case here:
        # 1. Activity queries below use this fact to take the comment as the target of
        #    the activity if one exists.
        # 2. Star query slices the first case away, since comments cannot be starred.
        return Case(
            When(comment__isnull=False, then=Concat(Value("comment "), "comment")),
            When(course__isnull=False, then=Concat(Value("course "), "course")),
            When(resource__isnull=False, then=Concat(Value("resource "), "resource")),
        )

    @staticmethod
    @lru_cache
    def __activity_type_name() -> Replace:
        return Replace(F("activity_type__name"), Value("_"), Value(" "))

    @staticmethod
    @lru_cache
    def __file_case(field: str) -> Case:
        # Ignore: Mypy thinks that `When` is getting multiple values for the `then` arg.
        return Case(
            When(**{field: ""}, then=None),  # type: ignore[misc]
            default=field,
        )


class Mutation(SkoleObjectType):
    my_data = MyDataMutation.Field()
