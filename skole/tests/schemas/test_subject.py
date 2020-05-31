from typing import List

from mypy.types import JsonDict

from skole.tests.helpers import SkoleSchemaTestCase


class SubjectSchemaTests(SkoleSchemaTestCase):
    authenticated = True

    # language=GraphQL
    subject_fields = """
        fragment subjectFields on SubjectObjectType {
            id
            name
        }
    """

    def query_subjects(self) -> List[JsonDict]:
        # language=GraphQL
        graphql = (
            self.subject_fields
            + """
            query Subjects {
                subjects {
                    ...subjectFields
                }
            }
            """
        )
        return self.execute(graphql)["subjects"]

    def query_subject(self, id: int) -> JsonDict:
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
        return self.execute(graphql, variables=variables)["subject"]

    def test_field_fragment(self) -> None:
        self.authenticated = False
        self.assert_field_fragment_matches_schema(self.subject_fields)

    def test_subjects(self) -> None:
        subjects = self.query_subjects()
        assert len(subjects) == 4
        # Subjects should be ordered alphabetically.
        assert subjects[0]["id"] == "3"
        assert subjects[0]["name"] == "Chemistry"
        assert subjects[1]["id"] == "1"
        assert subjects[1]["name"] == "Computer Engineering"

    def test_subject(self) -> None:
        subject = self.query_subject(id=1)
        assert subject["id"] == "1"
        assert subject["name"] == "Computer Engineering"

        assert self.query_subject(id=999) is None
