from skole.tests.helpers import SkoleSchemaTestCase, get_form_error
from skole.types import ID, JsonDict
from skole.utils.constants import Errors


class VoteSchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    def mutate_vote(
        self,
        *,
        status: int,
        comment: ID = None,
        thread: ID = None,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="vote",
            input_type="VoteMutationInput!",
            input={
                "status": status,
                "comment": comment,
                "thread": thread,
            },
            result="""
                vote {
                    id
                    status
                }
                targetScore
            """,
        )

    def test_vote_comment_ok(self) -> None:
        res = self.mutate_vote(status=1, comment=2)
        assert not res["errors"]
        assert res["targetScore"] == 1

        res = self.mutate_vote(status=-1, comment=2)
        assert not res["errors"]
        assert res["targetScore"] == -1

        res = self.mutate_vote(status=-1, comment=2)
        assert not res["errors"]
        assert res["targetScore"] == 0

        res = self.mutate_vote(status=1, comment=2)
        assert not res["errors"]
        assert res["targetScore"] == 1

        self.authenticated_user = 4
        res = self.mutate_vote(status=1, comment=2)
        assert not res["errors"]
        assert res["targetScore"] == 2

        self.authenticated_user = 5
        res = self.mutate_vote(status=1, comment=2)
        assert not res["errors"]
        assert res["targetScore"] == 3

        self.authenticated_user = 2

        res = self.mutate_vote(status=1, thread=2)
        assert not res["errors"]
        assert res["vote"]["status"] == 1
        assert res["targetScore"] == 1

    def test_vote_comment_error(self) -> None:
        # Can't use a status other than 1 or -1
        res = self.mutate_vote(status=10, comment=2)
        assert "is not a valid choice" in get_form_error(res)

        # Can't vote for own content.
        res = self.mutate_vote(status=1, comment=1)
        assert get_form_error(res) == Errors.VOTE_OWN_CONTENT

        # Can't have more than one target.
        res = self.mutate_vote(status=1, comment=1, thread=1)
        assert get_form_error(res) == Errors.MUTATION_INVALID_TARGET

    def test_vote_thread_ok(self) -> None:
        res = self.mutate_vote(status=1, thread=2)
        assert not res["errors"]
        assert res["targetScore"] == 1

        res = self.mutate_vote(status=1, thread=2)
        assert not res["errors"]
        assert res["targetScore"] == 0

        res = self.mutate_vote(status=-1, thread=2)
        assert not res["errors"]
        assert res["targetScore"] == -1

        res = self.mutate_vote(status=1, thread=2)
        assert not res["errors"]
        assert res["targetScore"] == 1

        self.authenticated_user = 4
        res = self.mutate_vote(status=1, thread=2)
        assert not res["errors"]
        assert res["targetScore"] == 2

        self.authenticated_user = 5
        res = self.mutate_vote(status=1, thread=2)
        assert not res["errors"]
        assert res["targetScore"] == 3
