from __future__ import annotations

from typing import Optional

from django.conf import settings

from skole.models import Activity
from skole.tests.helpers import SkoleSchemaTestCase, get_graphql_error
from skole.types import ID, JsonDict
from skole.utils.constants import Errors


class ActivitySchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    # language=GraphQL
    activity_fields = """
        fragment activityFields on ActivityObjectType {
            id
            description
            read
            causingUser {
                id
                username
                avatarThumbnail
            }
            comment {
                id
                thread {
                    slug
                }
            }
            badgeProgress {
                badge {
                    id
                    name
                    description
                    tier
                }
                progress
                steps
            }
        }
    """

    def query_activities(
        self,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        assert_error: bool = False,
    ) -> JsonDict:
        variables = {
            "page": page,
            "pageSize": page_size,
        }

        # language=GraphQL
        graphql = (
            self.activity_fields
            + """
            query Activities($page: Int, $pageSize: Int) {
                activities(page: $page, pageSize: $pageSize) {
                    page
                    pages
                    hasNext
                    hasPrev
                    count
                    objects {
                        ...activityFields
                    }
                }
            }
            """
        )

        return self.execute(graphql, variables=variables, assert_error=assert_error)

    def query_activity_preview(self, assert_error: bool = False) -> JsonDict:
        # language=GraphQL
        graphql = (
            self.activity_fields
            + """
            query ActivityPreview {
                activityPreview {
                    ...activityFields
                }
            }
            """
        )

        return self.execute(graphql, assert_error=assert_error)

    def mutate_mark_activity_as_read(self, id: str, read: bool) -> JsonDict:
        return self.execute_input_mutation(
            name="markActivityAsRead",
            input_type="MarkActivityAsReadMutationInput!",
            input={"id": id, "read": read},
            result="activity { ...activityFields }",
            fragment=self.activity_fields,
        )

    def mutate_mark_all_activities_as_read(self) -> JsonDict:
        result = """
            activities {
                page
                pages
                hasNext
                hasPrev
                count
                objects {
                    ...activityFields
                }
            }
        """

        return self.execute_non_input_mutation(
            name="markAllActivitiesAsRead",
            result=result,
            fragment=self.activity_fields,
        )

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.activity_fields)

    def test_activities(self) -> None:
        page_size = 2
        page = 1
        res = self.query_activities(page=page, page_size=page_size)
        assert len(res["objects"]) == page_size
        assert res["objects"][0]["id"] == "3"
        assert res["objects"][1]["id"] == "2"
        assert res["objects"][-1]["id"] == "2"
        assert res["count"] == 3
        assert res["page"] == page
        assert res["pages"] == 2
        assert res["hasNext"] is True
        assert res["hasPrev"] is False

        page = 2
        res = self.query_activities(page=page, page_size=page_size)
        assert res["objects"][0]["id"] == "1"
        assert len(res["objects"]) == 1  # Last page only has one result.
        assert res["count"] == 3
        assert res["page"] == page
        assert res["pages"] == 2
        assert res["hasNext"] is False
        assert res["hasPrev"] is True

        # Shouldn't work without auth.
        self.authenticated_user = None
        res = self.query_activities(page=page, page_size=page_size, assert_error=True)
        assert get_graphql_error(res) == Errors.AUTH_REQUIRED
        assert res["data"] == {"activities": None}

    def test_activity_preview(self) -> None:
        res = self.query_activity_preview()
        assert len(res) == 3 <= settings.ACTIVITY_PREVIEW_COUNT

        # Shouldn't work without auth.
        self.authenticated_user = None
        res = self.query_activity_preview(assert_error=True)
        assert get_graphql_error(res) == Errors.AUTH_REQUIRED
        assert res["data"] == {"activityPreview": None}

    def test_mark_activity_as_read(self) -> None:
        test_activity = Activity.objects.get(pk=1)
        assert not test_activity.read

        # Test marking activity as read.
        res = self.mutate_mark_activity_as_read(id=test_activity.pk, read=True)
        assert res["activity"]["read"]

        # Test marking activity as not read.
        res = self.mutate_mark_activity_as_read(id=test_activity.pk, read=False)
        assert not res["activity"]["read"]

    def test_mark_all_activities_as_read(self) -> None:
        # Ignore: Mypy expects a type of `Union[User, int, None]` for the `user` lookup.
        activities = Activity.objects.filter(user=self.authenticated_user)  # type: ignore[misc]

        for activity in activities:
            assert not activity.read

        res = self.mutate_mark_all_activities_as_read()

        assert res["activities"]["page"] == 1

        for activity in res["activities"]["objects"]:
            # Ignore: Mypy cannot infer the types from dict.
            assert activity["read"]  # type: ignore[index]
