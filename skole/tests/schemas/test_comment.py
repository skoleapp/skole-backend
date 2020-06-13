from typing import Optional

from mypy.types import JsonDict

from skole.models import Comment, Course, Resource
from skole.tests.helpers import (
    FileData,
    SkoleSchemaTestCase,
    get_form_error,
    get_graphql_error,
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
        self, *, text: str, attachment: str, file_data: FileData
    ) -> JsonDict:
        return self.execute_input_mutation(
            input_type="UpdateCommentMutationInput!",
            op_name="updateComment",
            input={"text": text, "attachment:": attachment},
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
        assert Comment.objects.get(pk=2).reply_comments.first().text == text  # type: ignore[union-attr]
        assert Comment.objects.get(pk=2).reply_comments.first().pk == int(comment["id"])  # type: ignore[union-attr]

        # Create a comment to a resource.
        res = self.mutate_create_comment(text=text, resource=2)
        comment = res["comment"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 2
        assert Resource.objects.get(pk=2).comments.count() == 1
        assert Resource.objects.get(pk=2).comments.first().text == text  # type: ignore[union-attr]
        assert Resource.objects.get(pk=2).comments.first().pk == int(comment["id"])  # type: ignore[union-attr]

        # Create a comment to a course.
        res = self.mutate_create_comment(text=text, course=2)
        comment = res["comment"]
        assert comment["text"] == text
        assert Comment.objects.count() == old_count + 3
        assert Course.objects.get(pk=2).comments.count() == 1
        assert Course.objects.get(pk=2).comments.first().text == text  # type: ignore[union-attr]
        assert Course.objects.get(pk=2).comments.first().pk == int(comment["id"])  # type: ignore[union-attr]

        # Can't create a comment with 2 targets.
        res = self.mutate_create_comment(text=text, course=1, resource=1)
        assert get_form_error(res) == ValidationErrors.MUTATION_INVALID_TARGET

        # Can't create a comment with 3 targets.
        res = self.mutate_create_comment(text=text, course=1, resource=1, comment=1)
        assert get_form_error(res) == ValidationErrors.MUTATION_INVALID_TARGET
        # Check that the comment count hasn't changed.
        assert Comment.objects.count() == old_count + 3

    def test_delete_comment(self) -> None:
        assert Comment.objects.filter(pk=1)
        res = self.mutate_delete_comment(id=1)
        assert res["message"] == Messages.COMMENT_DELETED
        assert not Comment.objects.filter(pk=1)

        res = self.mutate_delete_comment(id=1, assert_error=True)
        assert get_graphql_error(res) == "Comment matching query does not exist."

        res = self.mutate_delete_comment(id=2)
        assert get_form_error(res) == ValidationErrors.NOT_OWNER
