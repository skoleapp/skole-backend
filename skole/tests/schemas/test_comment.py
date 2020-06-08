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
    authenticated = True

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
            replyCount
            score
            vote {
                id
                status
            }
            modified
            created
        }
    """

    def mutate_delete_comment(self, *, id: ID, assert_error: bool = False) -> JsonDict:
        return self.execute_input_mutation(
            input_type="DeleteCommentMutationInput!",
            op_name="deleteComment",
            input={"id": id},
            result="message",
            assert_error=assert_error,
        )

    def test_field_fragment(self) -> None:
        self.authenticated = False
        self.assert_field_fragment_matches_schema(self.comment_fields)

    def test_delete_comment(self) -> None:
        assert Comment.objects.filter(pk=1)
        res = self.mutate_delete_comment(id=1)
        assert res["message"] == Messages.COMMENT_DELETED
        assert not Comment.objects.filter(pk=1)

        res = self.mutate_delete_comment(id=1, assert_error=True)
        assert get_graphql_error(res) == "Comment matching query does not exist."

        res = self.mutate_delete_comment(id=2)
        assert get_form_error(res) == ValidationErrors.NOT_OWNER
