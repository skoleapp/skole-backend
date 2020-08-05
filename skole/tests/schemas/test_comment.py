from typing import Optional

from django.core.files.uploadedfile import UploadedFile
from mypy.types import JsonDict

from skole.models import Comment, Course, Resource
from skole.tests.helpers import (
    FileData,
    SkoleSchemaTestCase,
    get_form_error,
    get_graphql_error,
    is_slug_match,
)
from skole.utils.constants import Messages, ValidationErrors
from skole.utils.types import ID


class CommentSchemaTests(SkoleSchemaTestCase):
    authenticated_user: Optional[int] = 2

    # language=GraphQL
    comment_fields = """
        fragment commentFields on CommentObjectType {
            id
            user {
                id
            }
            text
            attachment
            course {
                id
            }
            resource {
                id
            }
            comment {
                id
            }
            replyComments {
                id
            }
            score
            vote {
                id
                status
            }
            modified
            created
        }
    """

    def mutate_create_comment(
        self,
        *,
        text: str = "",
        attachment: str = "",
        course: ID = None,
        resource: ID = None,
        comment: ID = None,
        file_data: FileData = None,
    ) -> JsonDict:
        return self.execute_input_mutation(
            input_type="CreateCommentMutationInput!",
            op_name="createComment",
            input={
                "text": text,
                "attachment": attachment,
                "course": course,
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
            input_type="UpdateCommentMutationInput!",
            op_name="updateComment",
            input={"id": id, "text": text, "attachment": attachment},
            result="comment { ...commentFields }",
            fragment=self.comment_fields,
            file_data=file_data,
        )

    def mutate_delete_comment(self, *, id: ID, assert_error: bool = False) -> JsonDict:
        return self.execute_input_mutation(
            input_type="DeleteCommentMutationInput!",
            op_name="deleteComment",
            input={"id": id},
            result="message",
            assert_error=assert_error,
        )

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.comment_fields)

    def test_create_comment(self) -> None:
        # Create a comment which replies to a comment.
        old_count = Comment.objects.count()
        text = "Some text for the comment."
        res = self.mutate_create_comment(text=text, comment=2)
        comment = res["comment"]
        assert res["errors"] is None
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 1
        assert Comment.objects.get(pk=2).reply_comments.count() == 1
        assert Comment.objects.get(pk=2).reply_comments.first().text == text
        assert Comment.objects.get(pk=2).reply_comments.first().pk == int(comment["id"])

        # Create a comment to a resource.
        res = self.mutate_create_comment(text=text, resource=2)
        comment = res["comment"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 2
        assert Resource.objects.get(pk=2).comments.count() == 1
        assert Resource.objects.get(pk=2).comments.first().text == text
        assert Resource.objects.get(pk=2).comments.first().pk == int(comment["id"])

        # Create a comment to a course.
        res = self.mutate_create_comment(text=text, course=2)
        comment = res["comment"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 3
        assert Course.objects.get(pk=2).comments.count() == 1
        assert Course.objects.get(pk=2).comments.first().text == text
        assert Course.objects.get(pk=2).comments.first().pk == int(comment["id"])

        # Can't create a comment with 2 targets.
        res = self.mutate_create_comment(text=text, course=1, resource=1)
        assert get_form_error(res) == ValidationErrors.MUTATION_INVALID_TARGET

        # Can't create a comment with 3 targets.
        res = self.mutate_create_comment(text=text, course=1, resource=1, comment=1)
        assert get_form_error(res) == ValidationErrors.MUTATION_INVALID_TARGET
        # Check that the comment count hasn't changed.
        assert Comment.objects.count() == old_count + 3

        # Can't create a comment with no text and no attachment.
        res = self.mutate_create_comment(text="", attachment="", course=1)
        assert get_form_error(res) == ValidationErrors.COMMENT_EMPTY

    def test_update_comment(self) -> None:
        file_path = "media/uploads/attachments/test_attachment.png"
        new_text = "some new text"
        with open(file_path, "rb") as f:
            attachment = UploadedFile(f)
            res = self.mutate_update_comment(
                id=4,
                text=new_text,
                attachment="",
                file_data=[("attachment", attachment)],
            )
        assert is_slug_match("/" + file_path, res["comment"]["attachment"])
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

        # Can't update a comment to have no text and no attachment.
        res = self.mutate_update_comment(id=1, text="", attachment="")
        assert res["errors"] is not None
        assert res["comment"] is None

    def test_delete_comment(self) -> None:
        assert Comment.objects.filter(pk=1)
        res = self.mutate_delete_comment(id=1)
        assert res["message"] == Messages.COMMENT_DELETED
        assert not Comment.objects.filter(pk=1)

        res = self.mutate_delete_comment(id=1, assert_error=True)
        assert get_graphql_error(res) == "Comment matching query does not exist."

        res = self.mutate_delete_comment(id=2)
        assert get_form_error(res) == ValidationErrors.NOT_OWNER
