from typing import Optional

from skole.models import Comment, Resource, School, Thread
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
from skole.utils.constants import Messages, ValidationErrors


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
            thread {
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
        thread: ID = None,
        resource: ID = None,
        school: ID = None,
        assert_error: bool = False,
    ) -> JsonDict:
        variables = {
            "thread": thread,
            "resource": resource,
            "school": school,
        }

        # language=GraphQL
        graphql = (
            self.comment_fields
            + """
                query Discussion(
                    $thread: ID,
                    $resource: ID,
                    $school: ID
                ) {
                    discussion(
                        thread: $thread,
                        resource: $resource,
                        school: $school
                    ) {
                        ...commentFields
                    }
                }
            """
        )

        return self.execute(graphql, variables=variables, assert_error=assert_error)

    def mutate_create_comment(
        self,
        *,
        user: ID = 2,
        text: str = "",
        attachment: str = "",
        thread: ID = None,
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
                "thread": thread,
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
        # Create a reply comment.
        old_count = Comment.objects.count()
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

        # Create a comment to a resource.
        res = self.mutate_create_comment(text=text, resource=2)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 2
        assert Resource.objects.get(pk=2).comments.count() == 2
        assert get_last(Resource.objects.get(pk=2).comments).text == text
        assert get_last(Resource.objects.get(pk=2).comments).pk == int(comment["id"])

        # Create a comment to a thread.
        res = self.mutate_create_comment(text=text, thread=2)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 3
        assert Thread.objects.get(pk=2).comments.count() == 2
        assert get_last(Thread.objects.get(pk=2).comments).text == text
        assert get_last(Thread.objects.get(pk=2).comments).pk == int(comment["id"])

        # Create a comment to resource and thread.
        res = self.mutate_create_comment(text=text, thread=3, resource=15)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 4
        assert Resource.objects.get(pk=15).comments.count() == 1
        assert get_last(Resource.objects.get(pk=15).comments).text == text
        assert get_last(Resource.objects.get(pk=15).comments).pk == int(comment["id"])
        assert Thread.objects.get(pk=3).comments.count() == 2
        assert get_last(Thread.objects.get(pk=3).comments).text == text
        assert get_last(Thread.objects.get(pk=3).comments).pk == int(comment["id"])

        # Create a comment to a school.

        res = self.mutate_create_comment(text=text, school=1)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 5
        assert School.objects.get(pk=1).comments.count() == 2
        assert get_last(School.objects.get(pk=1).comments).text == text
        assert get_last(School.objects.get(pk=1).comments).pk == int(comment["id"])

        # Create a comment to thread and school.

        res = self.mutate_create_comment(text=text, thread=3, school=1)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 6
        assert Thread.objects.get(pk=3).comments.count() == 3
        assert get_last(Thread.objects.get(pk=3).comments).text == text
        assert get_last(Thread.objects.get(pk=3).comments).pk == int(comment["id"])
        assert School.objects.get(pk=1).comments.count() == 3
        assert get_last(School.objects.get(pk=1).comments).text == text
        assert get_last(School.objects.get(pk=1).comments).pk == int(comment["id"])

        # Create a comment with an attachment.
        with open_as_file(TEST_ATTACHMENT_PNG) as attachment:
            res = self.mutate_create_comment(
                text=text, thread=2, file_data=[("attachment", attachment)]
            )

        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert is_slug_match(UPLOADED_ATTACHMENT_PNG, comment["attachment"])
        assert comment["attachmentThumbnail"]
        assert Comment.objects.count() == old_count + 7

        self.authenticated_user = None

        # Create a comment without logging in
        res = self.mutate_create_comment(text=text, thread=3)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["text"] == text
        assert comment["thread"]["id"] == "3"
        assert comment["user"] is None
        assert Comment.objects.count() == old_count + 8

        # Can't add an attachment to the comment without logging in.
        with open_as_file(TEST_ATTACHMENT_PNG) as attachment:
            res = self.mutate_create_comment(
                text=text, thread=2, file_data=[("attachment", attachment)]
            )

        comment = res["comment"]
        # No need to return an error, frontend will anyways hide this option for
        # non-logged in users, backend just does the extra confirmation.
        assert not res["errors"]
        assert res["comment"]["attachment"] == ""  # Note that no attachment here.
        assert res["comment"]["text"] == text
        assert Comment.objects.count() == old_count + 9

        # Can't add an attachment to the comment without having a verified account.

        self.authenticated_user = 3
        assert not self.get_authenticated_user().verified

        with open_as_file(TEST_ATTACHMENT_PNG) as attachment:
            res = self.mutate_create_comment(
                text=text, thread=2, file_data=[("attachment", attachment)]
            )

        comment = res["comment"]
        # No need to return an error, frontend will anyways hide this option for
        # non-verified users, backend just does the extra confirmation.
        assert not res["errors"]
        assert res["comment"]["attachment"] == ""  # Note that no attachment here.
        assert res["comment"]["text"] == text
        assert Comment.objects.count() == old_count + 10

        self.authenticated_user = 2

        # Can't create a comment with no text and no attachment.
        res = self.mutate_create_comment(text="", attachment="", thread=1)
        assert get_form_error(res) == ValidationErrors.COMMENT_EMPTY

        # Check that the comment count hasn't changed.
        assert Comment.objects.count() == old_count + 10

        # Test creating anonymous comment as authenticated user.
        res = self.mutate_create_comment(user=None, text=text, thread=2)
        comment = res["comment"]
        assert not res["errors"]
        assert comment["user"] is None

        # Test that the author cannot be spoofed.
        res = self.mutate_create_comment(
            user=self.authenticated_user + 1, text=text, thread=2
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
        assert res["comment"]["thread"]["id"] == "1"
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
