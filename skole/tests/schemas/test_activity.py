from typing import Optional

from skole.models import Activity, ActivityType, Comment, Course, Resource, User
from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import JsonDict


class ActivitySchemaTests(SkoleSchemaTestCase):
    authenticated_user: Optional[int] = 2

    # language=GraphQL
    activity_fields = """
        fragment activityFields on ActivityObjectType {
            id
            description
            read
            targetUser {
                id
                username
                avatarThumbnail
            }
            course {
                id
            }
            resource {
                id
            }
            comment {
                id
            }
        }
    """

    def mutate_mark_activity_read(self, id: str, read: bool) -> JsonDict:
        return self.execute_input_mutation(
            name="markActivityRead",
            input_type="MarkActivityReadMutationInput!",
            input={"id": id, "read": read},
            result="activity { ...activityFields }",
            fragment=self.activity_fields,
        )

    def mutate_mark_all_activities_read(self) -> JsonDict:
        return self.execute_non_input_mutation(
            name="markAllActivitiesRead",
            result="activities { ...activityFields }",
            fragment=self.activity_fields,
        )

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.activity_fields)

    def test_mark_activity_read(self) -> None:
        testuser2 = User.objects.get(pk=2)
        course = Course.objects.get(pk=1)
        comment = Comment.objects.get(pk=1)
        activity_type = ActivityType.objects.get(pk=1)
        test_activity = Activity.objects.create(
            user=testuser2, activity_type=activity_type, course=course, comment=comment
        )

        assert not test_activity.read

        # Test marking activity as read.
        res = self.mutate_mark_activity_read(id=test_activity.pk, read=True)
        assert res["activity"]["description"] == activity_type.description
        assert res["activity"]["read"]
        assert res["activity"]["course"]["id"] == str(course.pk)
        assert res["activity"]["resource"] is None
        assert res["activity"]["comment"]["id"] == str(comment.pk)

        # Test marking activity as not read.
        res = self.mutate_mark_activity_read(id=test_activity.pk, read=False)
        assert res["activity"]["description"] == activity_type.description
        assert not res["activity"]["read"]
        assert res["activity"]["course"]["id"] == str(course.pk)
        assert res["activity"]["resource"] is None
        assert res["activity"]["comment"]["id"] == str(comment.pk)

        test_activity.delete()

    def test_mark_all_activities_read(self) -> None:
        testuser2 = User.objects.get(pk=2)
        resource1 = Resource.objects.get(pk=1)
        comment1 = Comment.objects.get(pk=2)
        resource2 = Resource.objects.get(pk=2)
        comment2 = Comment.objects.get(pk=3)
        activity_type1 = ActivityType.objects.get(pk=1)
        activity_type2 = ActivityType.objects.get(pk=2)

        test_activity1 = Activity.objects.create(
            user=testuser2,
            activity_type=activity_type1,
            resource=resource1,
            comment=comment1,
        )

        test_activity2 = Activity.objects.create(
            user=testuser2,
            activity_type=activity_type2,
            resource=resource2,
            comment=comment2,
        )

        assert not test_activity1.read
        assert not test_activity2.read

        res = self.mutate_mark_all_activities_read()

        assert res["activities"][0]["id"] == str(test_activity1.pk)
        assert res["activities"][0]["description"] == activity_type1.description
        assert res["activities"][0]["read"]
        assert res["activities"][0]["course"] is None
        assert res["activities"][0]["resource"]["id"] == str(resource1.pk)
        assert res["activities"][0]["comment"]["id"] == str(comment1.pk)

        assert res["activities"][1]["id"] == str(test_activity2.pk)
        assert res["activities"][1]["description"] == activity_type2.description
        assert res["activities"][1]["read"]
        assert res["activities"][1]["course"] is None
        assert res["activities"][1]["resource"]["id"] == str(resource2.pk)
        assert res["activities"][1]["comment"]["id"] == str(comment2.pk)

        test_activity1.delete()
        test_activity2.delete()
