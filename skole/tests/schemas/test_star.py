from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import ID, JsonDict


class StarSchemaTests(SkoleSchemaTestCase):
    authenticated_user: ID = 2

    def mutate_star(
        self,
        *,
        course: ID = None,
        resource: ID = None,
    ) -> JsonDict:
        return self.execute_input_mutation(
            name="star",
            input_type="StarMutationInput!",
            input={
                "course": course,
                "resource": resource,
            },
            result="starred",
        )

    def test_star(self) -> None:
        res = self.mutate_star(course=1)
        assert not res["errors"]
        assert res["starred"] is False  # It was already starred so should be flipped.

        res = self.mutate_star(course=1)
        assert not res["errors"]
        assert res["starred"] is True

        res = self.mutate_star(resource=1)
        assert not res["errors"]
        assert res["starred"] is False  # It was already starred so should be flipped.

        res = self.mutate_star(resource=3)
        assert not res["errors"]
        assert res["starred"] is True
