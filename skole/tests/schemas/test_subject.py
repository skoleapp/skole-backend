from typing import List, cast

from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import ID, JsonDict


class SubjectSchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    subject_fields = """
        fragment subjectFields on SubjectObjectType {
            id
            name
            courseCount
            resourceCount
        }
    """

    def query_autocomplete_subjects(self, name: str = "") -> List[JsonDict]:
        # language=GraphQL
        graphql = (
            self.subject_fields
            + """
            query AutocompleteSubjects($name: String) {
                autocompleteSubjects(name: $name) {
                    ...subjectFields
                }
            }
            """
        )
        return cast(List[JsonDict], self.execute(graphql))

    def query_subject(self, *, id: ID) -> JsonDict:
        variables = {"id": id}

        # language=GraphQL
        graphql = (
            self.subject_fields
            + """
            query Subject($id: ID!) {
                subject(id: $id) {
                    ...subjectFields
                }
            }
            """
        )
        return self.execute(graphql, variables=variables)

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.subject_fields)

    def test_autocomplete_subjects(self) -> None:
        subjects = self.query_autocomplete_subjects()

        # By default, subjects are ordered by the amount of courses.
        assert subjects[0] == self.query_subject(id=1)  # Most courses.
        assert subjects[1] == self.query_subject(id=2)  # 2nd most courses.
        assert subjects[2] == self.query_subject(id=3)  # 3rd most courses.

        # Query subjects by name.
        res = self.query_autocomplete_subjects("Computer")
        assert len(res) == 4
        assert res[0] == self.query_subject(id=1)  # Compututer Engineering.
        assert res[1] == self.query_subject(id=2)  # Computer Science.

        # TODO: Tests that no more than the maximum limit of results are returned.
        # Currently we don't have enough test schools to exceed the limit.

    def test_subject(self) -> None:
        subject = self.query_subject(id=1)
        assert subject["id"] == "1"
        assert subject["name"] == "Computer Engineering"
        assert subject["courseCount"] == 12
        assert subject["resourceCount"] == 3

        assert self.query_subject(id=999) is None
