from mypy.types import JsonDict

from skole.models import Comment
from skole.tests.helpers import SkoleSchemaTestCase
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

    def mutate_delete_comment(self, *, id: ID) -> JsonDict:
        return self.execute_input_mutation(
            input_type="DeleteCommentMutationInput!",
            op_name="deleteComment",
            input={"id": id},
            result="message",
        )

    def test_field_fragment(self) -> None:
        self.authenticated = False
        self.assert_field_fragment_matches_schema(self.comment_fields)

    def test_delete_comment(self) -> None:
        assert Comment.objects.filter(pk=1)
        res = self.mutate_delete_comment(id=1)
        assert res["message"] == Messages.COMMENT_DELETED
        assert not Comment.objects.filter(pk=1)

        self.should_error = True
        res = self.mutate_delete_comment(id=1)
        assert res["errors"][0]["message"] == "Comment matching query does not exist."

        self.should_error = False
        res = self.mutate_delete_comment(id=2)
        assert res["errors"][0]["messages"][0] == ValidationErrors.NOT_OWNER
