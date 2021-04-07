from __future__ import annotations

import datetime
import functools
import io
import itertools
import json
import math
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, cast

import graphene
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Case, CharField, F, QuerySet, Value, When
from django.db.models.fields.files import FieldFile
from django.db.models.functions import Concat, Replace
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils import timezone, translation
from django.utils.html import strip_tags
from graphene_django.types import ErrorType

from skole.models import (
    Activity,
    Badge,
    Comment,
    DailyVisit,
    SkoleModel,
    Star,
    Thread,
    User,
    Vote,
)
from skole.overridden import login_required
from skole.schemas.base import SkoleObjectType
from skole.types import JsonList, ResolveInfo
from skole.utils.constants import Errors, Messages, Notifications, VoteConstants
from skole.utils.files import override_s3_file_age
from skole.utils.shortcuts import to_form_error

if TYPE_CHECKING:
    # https://stackoverflow.com/a/63520010/9835872
    from django.db.models.query import (  # pylint: disable=no-name-in-module
        ValuesQuerySet,
    )


class DjangoQuerySetJSONEncoder(DjangoJSONEncoder):
    """JSON encoder which can serialize QuerySets."""

    def default(self, o: Any) -> Any:
        if isinstance(o, QuerySet):
            return list(o)
        else:
            return super().default(o)


class JSONString(graphene.JSONString):
    """A graphene JSON field which handles serializing datetimes, QuerySets and more."""

    @staticmethod
    def serialize(dt: Any) -> str:
        return json.dumps(dt, cls=DjangoQuerySetJSONEncoder)


class MyDataMutation(SkoleObjectType, graphene.Mutation):
    """Email the user with a link to a zip file containing **all** of their data."""

    # Can't inherit `SkoleCreateUpdateMutationMixin` since this doesn't use a form.

    # Can't use `SuccessMessageMixin` since it only works with `BaseDjangoFormMutation`.
    success_message = graphene.String()

    errors = graphene.List(ErrorType, default_value=[])

    @classmethod
    @login_required
    def mutate(cls, root: None, info: ResolveInfo) -> MyDataMutation:
        # TODO: this could use fire-and-forget style async execution.
        user = cast(User, info.context.user)
        if remaining := cls.__time_until_can_request_again(user):
            return cls(errors=to_form_error(Errors.RATE_LIMITED.format(remaining)))

        with translation.override(settings.LANGUAGE_CODE):
            # Everything in EN for consistency.
            data = {
                # Model fields
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "title": user.title,
                "bio": user.bio,
                "avatar": user.avatar.name if user.avatar else None,
                "score": user.score,
                "verified": user.verified,
                "is_active": user.is_active,
                "last_login": user.last_login,
                "modified": user.modified,
                "created": user.created,
                "last_my_data_query": user.last_my_data_query,
                # Related models
                "last_visit": cls._last_visit(user),
                "daily_visits": cls._daily_visits(user),
                "created_comments": cls._created_comments(user),
                "created_threads": cls._created_threads(user),
                "badges": cls._badges(user),
                "badgeProgresses": cls._badge_progresses(user),
                "selectedBadgeProgress": cls._selected_badge_progress(user),
                "votes": cls._votes(user),
                "stars": cls._stars(user),
                "activities": cls._activities(user),
                "caused_activities": cls._caused_activities(user),
            }
        json_data = json.dumps(
            data,
            indent=4,
            ensure_ascii=False,
            cls=DjangoQuerySetJSONEncoder,
        )
        data_url = cls.__create_zip(user, json_data, request=info.context)
        cls.__send_email(user, data_url)
        return cls(success_message=Messages.DATA_REQUEST_RECEIVED)

    @classmethod
    def _created_comments(cls, user: User) -> ValuesQuerySet[Comment, Any]:
        return user.comments.values(
            "id",
            "text",
            "modified",
            "created",
            target=cls.__target_case(Comment),
            uploaded_file=cls.__file_case("file"),
            uploaded_image=cls.__file_case("image"),
        )

    @classmethod
    def _created_threads(cls, user: User) -> ValuesQuerySet[Thread, Any]:
        return user.created_threads.values(
            "id",
            "title",
            "text",
            "modified",
            "created",
            uploaded_image=cls.__file_case("image"),
        )

    @classmethod
    def _activities(cls, user: User) -> ValuesQuerySet[Activity, Any]:
        return user.activities.values(
            "id",
            "read",
            target=cls.__target_case(Activity),
            type=cls.__activity_type_name(),
        )

    @classmethod
    def _caused_activities(cls, user: User) -> ValuesQuerySet[Activity, Any]:
        return user.caused_activities.values(
            "id",
            "read",
            type=cls.__activity_type_name(),
            target=cls.__target_case(Activity),
        )

    @classmethod
    def _votes(cls, user: User) -> ValuesQuerySet[Vote, Any]:
        return user.votes.values(
            "id",
            target=cls.__target_case(Vote),
            vote=Case(
                *(
                    When(status=value, then=Value(display))
                    for value, display in VoteConstants.STATUS
                ),
                output_field=CharField(),
            ),
        )

    @classmethod
    def _stars(cls, user: User) -> QuerySet[Star]:
        return user.stars.annotate(
            target=cls.__target_case(Star),
        ).values_list("target", flat=True)

    @staticmethod
    def _badges(user: User) -> QuerySet[Badge]:
        return (
            Badge.objects.translated()
            .filter(
                badge_progresses__user=user, badge_progresses__acquired__isnull=False
            )
            .values_list("translations__name", flat=True)
        )

    @staticmethod
    def _badge_progresses(user: User) -> JsonList:
        badge_progresses = (
            user.get_or_create_badge_progresses()
            .filter(badge__translations__language_code=settings.LANGUAGE_CODE)
            .values_list("badge__translations__name", "progress", "badge__steps")
        )

        return [
            {"badge": badge, "progress": f"{progress} / {steps}"}
            for (badge, progress, steps) in badge_progresses
        ]

    @staticmethod
    def _selected_badge_progress(user: User) -> str:
        return (
            user.selected_badge_progress.badge.name
            if user.selected_badge_progress
            else None
        )

    @staticmethod
    def _uploaded_files(user: User) -> set[FieldFile]:
        # Objects basically shouldn't have duplicate files, but our test data
        # at least has those, so better to filter them away with a `set`.
        return {
            file
            for file in itertools.chain(
                (comment.file for comment in user.comments.all()),
                (comment.image for comment in user.comments.all()),
                (user.avatar,),
            )
            if file
        }

    @staticmethod
    def _last_visit(user: User) -> Optional[datetime.datetime]:
        return (
            DailyVisit.objects.filter(user=user)
            .order_by("pk")
            .values_list("last_visit", flat=True)
            .last()
        )

    @staticmethod
    def _daily_visits(user: User) -> ValuesQuerySet[DailyVisit, Any]:
        return (
            DailyVisit.objects.filter(user=user).order_by("pk").values("date", "visits")
        )

    @classmethod
    def __create_zip(cls, user: User, json_data: str, request: HttpRequest) -> str:
        assert user.last_my_data_query is not None  # Cannot be `None` anymore.

        file = Path(
            f"{user.username}_data_{user.last_my_data_query.strftime('%Y%m%d')}.zip"
        )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as f:
            for uploaded in cls._uploaded_files(user):
                f.writestr(f"{file.stem}/{uploaded.name}", uploaded.read())

            f.writestr(f"{file.stem}/data.json", json_data)

        with override_s3_file_age(settings.MY_DATA_FILE_AVAILABLE_FOR):
            storage_name = default_storage.save(
                name=f"generated/my_data/{file.name}", content=buffer
            )
            url = default_storage.url(name=storage_name)

        if settings.DEBUG:
            # In dev env this is just the file path, so let's make it an absolute one.
            return request.build_absolute_uri(url)
        else:
            # In production this will already be a full absolute S3 URL.
            return url

    @classmethod
    def __send_email(cls, user: User, data_url: str) -> None:
        html_message = render_to_string(
            "email/my_data.html",
            context={
                "user": user,
                "url": data_url,
                "days": settings.MY_DATA_FILE_AVAILABLE_FOR.days,
            },
        )
        mail = EmailMultiAlternatives(
            subject=Notifications.MY_DATA_SUBJECT,
            body=strip_tags(html_message),
            from_email=settings.EMAIL_ADDRESS,
            to=[user.email],
            connection=get_connection(),
        )
        mail.attach_alternative(html_message, "text/html")
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
    @functools.cache
    def __target_case(model: type[SkoleModel]) -> Case:
        cases = {
            "comment": When(
                comment__isnull=False, then=Concat(Value("comment "), "comment")
            ),
            "thread": When(
                thread__isnull=False, then=Concat(Value("thread "), "thread")
            ),
        }
        return Case(
            *(value for key, value in cases.items() if hasattr(model, key)),
            output_field=CharField(),
        )

    @staticmethod
    @functools.cache
    def __activity_type_name() -> Replace:
        return Replace(F("activity_type__identifier"), Value("_"), Value(" "))

    @staticmethod
    @functools.cache
    def __file_case(field: str) -> Case:
        return Case(When(**{field: ""}, then=None), default=field)


class Mutation(SkoleObjectType):
    my_data = MyDataMutation.Field()
