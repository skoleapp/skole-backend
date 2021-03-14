from typing import Optional

from django.conf import settings
from django.core import mail
from django.test import override_settings

from skole.models import Activity, Comment, Course, Resource, School
from skole.tests.helpers import (
    TEST_ATTACHMENT_PNG,
    UPLOADED_ATTACHMENT_PNG,
    FileData,
    SkoleSchemaTestCase,
    get_form_error,
    get_graphql_error,
    get_last,
    is_slug_match,
    open_as_file,
)
from skole.types import ID, JsonDict
from skole.utils.constants import Email, Messages, ValidationErrors


class CommentSchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    # language=GraphQL
    comment_fields = """
        fragment commentFields on CommentObjectType {
            id
            text
            attachment
            attachmentThumbnail
            score
            modified
            created
            replyCount
            user {
                id
            }
            course {
                id
            }
            resource {
                id
            }
            school {
                id
            }
            comment {
                id
            }
            replyComments {
                id
            }
            vote {
                id
                status
            }
        }
    """

    def query_comments(
        self,
        *,
        user: str = "",
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        assert_error: bool = False,
    ) -> JsonDict:
        variables = {
            "user": user,
            "page": page,
            "pageSize": page_size,
        }

        # language=GraphQL
        graphql = (
            self.comment_fields
            + """
                query Comments (
                    $user: String,
                    $page: Int,
                    $pageSize: Int
                ) {
                    comments (
                        user: $user,
                        page: $page,
                        pageSize: $pageSize
                    ) {
                        page
                        pages
                        hasNext
                        hasPrev
                        count
                        objects {
                            ...commentFields
                        }
                    }
                }
            """
        )

        return self.execute(graphql, variables=variables, assert_error=assert_error)

    def query_discussion(
        self,
        *,
        course: ID = None,
        resource: ID = None,
        school: ID = None,
        assert_error: bool = False,
    ) -> JsonDict:
        variables = {
            "course": course,
            "resource": resource,
            "school": school,
        }

        # language=GraphQL
        graphql = (
            self.comment_fields
            + """
                query Discussion(
                    $course: ID,
                    $resource: ID,
                    $school: ID
                ) {
                    discussion(
                        course: $course,
                        resource: $resource,
                        school: $school
                    ) {
                        ...commentFields
                    }
                }
            """
        )

        return self.execute(graphql, variables=variables, assert_error=assert_error)

    def query_discussion_suggestions(
        self,
        *,
        assert_error: bool = False,
    ) -> list[JsonDict]:
        # language=GraphQL
        graphql = """
            query DiscussionSuggestions {
                discussionSuggestions {
                    ... on CourseObjectType {
                        id
                        courseName: name
                        codes
                    }
                    ... on ResourceObjectType {
                        id
                        title
                    }
                    ... on SchoolObjectType {
                        id
                        name
                    }
                }
            }
        """

        return self.execute(graphql, assert_error=assert_error)

    def mutate_create_comment(
        self,
        *,
        user: ID = 2,
        text: str = "",
        attachment: str = "",
        course: ID = None,
        resource: ID = None,
        school: ID = None,
        comment: ID = None,
        file_data: FileData = None,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="createComment",
            input_type="CreateCommentMutationInput!",
            input={
                "user": user,
                "text": text,
                "attachment": attachment,
                "course": course,
                "school": school,
                "resource": resource,
                "comment": comment,
            },
            result="comment { ...commentFields }",
            fragment=self.comment_fields,
            file_data=file_data,
        )

    def mutate_update_comment(
        self,
        *,
        id: ID,
        text: str = "",
        attachment: str = "",
        file_data: FileData = None,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="updateComment",
            input_type="UpdateCommentMutationInput!",
            input={"id": id, "text": text, "attachment": attachment},
            result="comment { ...commentFields }",
            fragment=self.comment_fields,
            file_data=file_data,
        )

    def mutate_delete_comment(self, *, id: ID, assert_error: bool = False) -> JsonDict:
        return self.execute_input_mutation(
            name="deleteComment",
            input_type="DeleteCommentMutationInput!",
            input={"id": id},
            result="successMessage",
            assert_error=assert_error,
        )

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.comment_fields)

    def test_create_comment(self) -> None:  # pylint: disable=too-many-statements
        # Create a reply comment to a comment of another user.
        old_count = Comment.objects.count()
        old_activity_count = 3
        text = "Some text for the comment."
        res = self.mutate_create_comment(text=text, comment=2)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 1
        assert Comment.objects.get(pk=2).reply_comments.count() == 1
        assert Comment.objects.get(pk=2).reply_comments.get().text == text
        assert Comment.objects.get(pk=2).reply_comments.get().pk == int(comment["id"])
        assert comment["user"]["id"] == "2"

        assert Activity.objects.count() == old_activity_count + 1
        assert len(mail.outbox) == 1

        # Create a reply comment to own comment.
        res = self.mutate_create_comment(text=text, comment=1)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 2
        assert Comment.objects.get(pk=1).reply_comments.count() == 1
        assert Comment.objects.get(pk=1).reply_comments.get().text == text
        assert Comment.objects.get(pk=1).reply_comments.get().pk == int(comment["id"])
        assert comment["user"]["id"] == "2"

        assert Activity.objects.count() == old_activity_count + 1
        assert len(mail.outbox) == 1

        # Create a comment to a resource of another user.
        res = self.mutate_create_comment(text=text, resource=2)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 3
        assert Resource.objects.get(pk=2).comments.count() == 2
        assert get_last(Resource.objects.get(pk=2).comments).text == text
        assert get_last(Resource.objects.get(pk=2).comments).pk == int(comment["id"])

        assert Activity.objects.count() == old_activity_count + 2
        activity = Activity.objects.get(resource=2)
        assert len(mail.outbox) == 2
        sent = mail.outbox[1]
        assert sent.from_email == settings.EMAIL_ADDRESS
        assert sent.to == [activity.user.email]
        assert sent.subject == Email.EMAIL_NOTIFICATION_SUBJECT.format(
            activity.target_user, activity.activity_type.description
        )

        # Create a comment to own resource.
        res = self.mutate_create_comment(text=text, resource=1)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 4
        assert Resource.objects.get(pk=1).comments.count() == 5
        assert get_last(Resource.objects.get(pk=1).comments).text == text
        assert get_last(Resource.objects.get(pk=1).comments).pk == int(comment["id"])
        assert Activity.objects.count() == old_activity_count + 2
        assert len(mail.outbox) == 2

        # Create a comment to a course of another user.
        res = self.mutate_create_comment(text=text, course=2)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 5
        assert Course.objects.get(pk=2).comments.count() == 2
        assert get_last(Course.objects.get(pk=2).comments).text == text
        assert get_last(Course.objects.get(pk=2).comments).pk == int(comment["id"])

        assert Activity.objects.count() == old_activity_count + 3
        activity = Activity.objects.get(course=2)
        assert len(mail.outbox) == 3
        sent = mail.outbox[2]
        assert sent.from_email == settings.EMAIL_ADDRESS
        assert sent.to == [activity.user.email]
        assert sent.subject == Email.EMAIL_NOTIFICATION_SUBJECT.format(
            activity.target_user, activity.activity_type.description
        )

        # Create a comment to own course.
        res = self.mutate_create_comment(text=text, course=1)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 6
        assert Course.objects.get(pk=1).comments.count() == 9
        assert get_last(Course.objects.get(pk=1).comments).text == text
        assert get_last(Course.objects.get(pk=1).comments).pk == int(comment["id"])
        assert Activity.objects.count() == old_activity_count + 3
        assert len(mail.outbox) == 3

        # Create a comment to resource and course of another user.
        res = self.mutate_create_comment(text=text, course=3, resource=15)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 7
        assert Resource.objects.get(pk=15).comments.count() == 1
        assert get_last(Resource.objects.get(pk=15).comments).text == text
        assert get_last(Resource.objects.get(pk=15).comments).pk == int(comment["id"])
        assert Course.objects.get(pk=3).comments.count() == 2
        assert get_last(Course.objects.get(pk=3).comments).text == text
        assert get_last(Course.objects.get(pk=3).comments).pk == int(comment["id"])

        assert Activity.objects.count() == old_activity_count + 5
        assert len(mail.outbox) == 5

        course_comment_activity = Activity.objects.get(course=3)
        sent = mail.outbox[3]
        assert sent.from_email == settings.EMAIL_ADDRESS
        assert sent.to == [course_comment_activity.user.email]
        assert sent.subject == Email.EMAIL_NOTIFICATION_SUBJECT.format(
            course_comment_activity.target_user,
            course_comment_activity.activity_type.description,
        )

        resource_comment_activity = Activity.objects.get(resource=15)
        sent = mail.outbox[4]
        assert sent.from_email == settings.EMAIL_ADDRESS
        assert sent.to == [resource_comment_activity.user.email]
        assert sent.subject == Email.EMAIL_NOTIFICATION_SUBJECT.format(
            resource_comment_activity.target_user,
            resource_comment_activity.activity_type.description,
        )

        # Create a comment to a school.

        res = self.mutate_create_comment(text=text, school=1)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 8
        assert School.objects.get(pk=1).comments.count() == 2
        assert get_last(School.objects.get(pk=1).comments).text == text
        assert get_last(School.objects.get(pk=1).comments).pk == int(comment["id"])

        # Create a comment with an attachment.
        with open_as_file(TEST_ATTACHMENT_PNG) as attachment:
            res = self.mutate_create_comment(
                text=text, course=2, file_data=[("attachment", attachment)]
            )

        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert is_slug_match(UPLOADED_ATTACHMENT_PNG, comment["attachment"])
        assert comment["attachmentThumbnail"]
        assert Comment.objects.count() == old_count + 9

        self.authenticated_user = None

        # Create a comment without logging in
        res = self.mutate_create_comment(text=text, course=3)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert comment["course"]["id"] == "3"
        assert comment["user"] is None
        assert Comment.objects.count() == old_count + 10

        # Can't add an attachment to the comment without logging in.
        with open_as_file(TEST_ATTACHMENT_PNG) as attachment:
            res = self.mutate_create_comment(
                text=text, course=2, file_data=[("attachment", attachment)]
            )

        comment = res["comment"]
        # No need to return an error, frontend will anyways hide this option for
        # non-logged in users, backend just does the extra confirmation.
        assert not res["errors"]
        assert res["comment"]["attachment"] == ""  # Note that no attachment here.
        assert res["comment"]["text"] == text
        assert Comment.objects.count() == old_count + 11

        # Can't add an attachment to the comment without having a verified account.

        self.authenticated_user = 3
        assert not self.get_authenticated_user().verified

        with open_as_file(TEST_ATTACHMENT_PNG) as attachment:
            res = self.mutate_create_comment(
                text=text, course=2, file_data=[("attachment", attachment)]
            )

        comment = res["comment"]
        # No need to return an error, frontend will anyways hide this option for
        # non-verified users, backend just does the extra confirmation.
        assert not res["errors"]
        assert res["comment"]["attachment"] == ""  # Note that no attachment here.
        assert res["comment"]["text"] == text
        assert Comment.objects.count() == old_count + 12

        self.authenticated_user = 2

        # Can't create a comment with no text and no attachment.
        res = self.mutate_create_comment(text="", attachment="", course=1)
        assert get_form_error(res) == ValidationErrors.COMMENT_EMPTY

        # Check that the comment count hasn't changed.
        assert Comment.objects.count() == old_count + 12

        # Test creating anonymous comment as authenticated user.
        res = self.mutate_create_comment(user=None, text=text, course=2)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["user"] is None

        # Test that the author cannot be spoofed.
        res = self.mutate_create_comment(
            user=self.authenticated_user + 1, text=text, course=2
        )
        comment = res["comment"]
        assert not res["errors"]
        assert comment["user"] is None

    def test_update_comment(self) -> None:
        new_text = "some new text"

        with open_as_file(TEST_ATTACHMENT_PNG) as attachment:
            res = self.mutate_update_comment(
                id=4,
                text=new_text,
                attachment="",
                file_data=[("attachment", attachment)],
            )

        assert is_slug_match(UPLOADED_ATTACHMENT_PNG, res["comment"]["attachment"])
        assert res["comment"]["text"] == new_text
        assert res["comment"]["course"]["id"] == "1"
        assert res["comment"]["resource"] is None
        assert res["comment"]["comment"] is None

        # Clear attachment from comment.
        comment = Comment.objects.get(pk=1)
        assert comment.attachment
        res = self.mutate_update_comment(id=1, text=comment.text, attachment="")
        assert res["comment"]["attachment"] == ""
        assert not Comment.objects.get(pk=1).attachment

        # Can't update someone else's comment.
        res = self.mutate_update_comment(id=2, text=new_text)
        assert get_form_error(res) == ValidationErrors.NOT_OWNER

        # Can't update attachment when account is not verified.

        self.authenticated_user = 3
        assert not self.get_authenticated_user().verified

        with open_as_file(TEST_ATTACHMENT_PNG) as attachment:
            res = self.mutate_update_comment(
                id=2,
                text=new_text,
                attachment="",
                file_data=[("attachment", attachment)],
            )

        comment = res["comment"]
        # No need to return an error, frontend will anyways hide this option for
        # non-verified users, backend just does the extra confirmation.
        assert not res["errors"]
        assert res["comment"]["attachment"] == ""  # Note that no attachment here.
        assert res["comment"]["text"] == new_text

        # Can't update a comment to have no text and no attachment.
        res = self.mutate_update_comment(id=1, text="", attachment="")
        assert res["errors"] is not None
        assert res["comment"] is None

    def test_delete_comment(self) -> None:
        old_count = Comment.objects.count()

        assert Comment.objects.filter(pk=1)
        res = self.mutate_delete_comment(id=1)
        assert res["successMessage"] == Messages.COMMENT_DELETED
        assert not Comment.objects.filter(pk=1)
        assert Comment.objects.count() == old_count - 1

        res = self.mutate_delete_comment(id=1, assert_error=True)
        assert get_graphql_error(res) == "Comment matching query does not exist."

        res = self.mutate_delete_comment(id=2)
        assert get_form_error(res) == ValidationErrors.NOT_OWNER

        assert Comment.objects.count() == old_count - 1

    def test_comments(self) -> None:
        page = 1
        page_size = 1

        # Test that only comments of the correct user are returned.

        user = "testuser2"  # Slug for `self.authenticated_user`.

        res = self.query_comments(user=user, page=page, page_size=page_size)

        assert len(res["objects"]) == page_size

        for comment in res["objects"]:
            assert int(comment["user"]["id"]) == self.authenticated_user

        assert res["count"] == 17
        assert res["page"] == page
        assert res["pages"] == 17
        assert res["hasNext"] is True
        assert res["hasPrev"] is False

        # Test for some user that has created no comments.

        page = 1
        res = self.query_comments(user="testuser10", page=page, page_size=page_size)
        assert res["count"] == 0
        assert res["page"] == page
        assert res["pages"] == 1
        assert res["hasNext"] is False
        assert res["hasPrev"] is False

    def test_discussion(self) -> None:
        # Test that only comments of the correct course are returned.

        course = 1
        res = self.query_discussion(course=course)

        # Ignore: Mypy expects a type `Union[int, slice]` for the course ID field.
        for comment in res:
            assert int(comment["course"]["id"]) == course  # type: ignore[index]

        # Test for some course that has created no comments.

        course = 22
        res = self.query_discussion(course=course)
        assert len(res) == 0

        # Test that only comments of the correct resource are returned.

        resource = 1
        res = self.query_discussion(resource=resource)

        # Ignore: Mypy expects a type `Union[int, slice]` for the resource ID field.
        for comment in res:
            assert int(comment["resource"]["id"]) == resource  # type: ignore[index]

        # Test for some resource that has created no comments.

        resource = 22
        res = self.query_discussion(resource=resource)
        assert len(res) == 0

        # Test that only comments of the correct school are returned.

        school = 1
        res = self.query_discussion(school=school)

        # Ignore: Mypy expects a type `Union[int, slice]` for the school ID field.
        for comment in res:
            assert int(comment["school"]["id"]) == school  # type: ignore[index]

        # Test for some resource that has created no comments.

        school = 2
        res = self.query_discussion(school=school)
        assert len(res) == 0

    def test_discussion_suggestions(self) -> None:
        res = self.query_discussion_suggestions()
        assert len(res) <= settings.DISCUSSION_SUGGESTIONS_COUNT
        # User's own school should be the first suggestion.
        # Ignore: Mypy doesn't cannot know that `user.school` is not None here.
        assert res[0]["id"] == str(self.get_authenticated_user().school.pk)  # type: ignore[union-attr]
        assert res[0]["name"] == "University of Turku"
        assert res[1]["name"] == "Turku University of Applied Sciences"
        assert res[2]["courseName"] == "Test Engineering Course 1"
        # A few courses and resources are tied for the second place, since we don't
        # order the tied scores base d on the primary keys (to reduce query overhead),
        # the order of the results is not exactly stable and we can't test for exact match
        # here. It's just important that the second result is distinct from the first.
        assert res[3]["courseName"] != "Test Engineering Course 1"
        assert res[4]["title"] == "Sample Exam 1"
        assert res[5]["title"] != "Sample Exam 1"

        # Check that no duplicates are ever returned.
        with override_settings(DISCUSSION_SUGGESTIONS_COUNT=1000):
            res = self.query_discussion_suggestions()
            assert len(res) == len(
                {
                    (tuple(x) if isinstance(x, list) else x for x in elem.items())
                    for elem in res
                }
            )

        # Test that anonymous users cannot query discussion suggestions.
        self.authenticated_user = None
        res = self.query_discussion_suggestions(assert_error=True)
        assert "permission" in get_graphql_error(res)
