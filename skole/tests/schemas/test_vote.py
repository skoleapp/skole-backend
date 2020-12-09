from skole.tests.helpers import SkoleSchemaTestCase, get_form_error
from skole.types import ID, JsonDict
from skole.utils.constants import ValidationErrors


class VoteSchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    def mutate_vote(
        self,
        *,
        status: int,
        comment: ID = None,
        course: ID = None,
        resource: ID = None,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="vote",
            input_type="VoteMutationInput!",
            input={
                "status": status,
                "comment": comment,
                "course": course,
                "resource": resource,
            },
            result="vote { id status } targetScore",
        )

    def test_vote_ok(self) -> None:
        res = self.mutate_vote(status=1, comment=2)
        assert not res["errors"]
        assert res["targetScore"] == 1

        res = self.mutate_vote(status=-1, comment=2)
        assert not res["errors"]
        assert res["targetScore"] == -1

        res = self.mutate_vote(status=-1, comment=2)
        assert not res["errors"]
        assert res["targetScore"] == 0

        res = self.mutate_vote(status=1, resource=3)
        assert not res["errors"]
        assert res["targetScore"] == 1

        res = self.mutate_vote(status=1, course=2)
        assert not res["errors"]
        assert res["vote"]["status"] == 1
        assert res["targetScore"] == 1

    def test_vote_error(self) -> None:
        # Can't use a status other than 1 or -1
        res = self.mutate_vote(status=10, comment=2)
        assert "is not a valid choice" in get_form_error(res)

        # Can't vote for own content.
        res = self.mutate_vote(status=1, comment=1)
        assert get_form_error(res) == ValidationErrors.VOTE_OWN_CONTENT

        # Can't have more than one target.
        res = self.mutate_vote(status=1, comment=1, resource=3)
        assert get_form_error(res) == ValidationErrors.MUTATION_INVALID_TARGET
