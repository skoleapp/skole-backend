from typing import List

from mypy.types import JsonDict

from tests.test_utils import SchemaTestCase


class SchoolSchemaTests(SchemaTestCase):
    authenticated = True

    # language=GraphQL
    school_fields = """
        fragment schoolFields on SchoolObjectType {
            id
            name
            subjects {
              id
            }
            courses {
              id
            }
            subjectCount
            courseCount
            schoolType
            country
            city
        }
    """

    def query_schools(self) -> List[JsonDict]:
        # language=GraphQL
        graphql = (
            self.school_fields
            + """
            query Schools {
                schools {
                    ...schoolFields
                }
            }
        """
        )
        return self.execute(graphql)["schools"]

    def query_school(self, id: int) -> JsonDict:
        variables = {"id": id}

        # language=GraphQL
        graphql = (
            self.school_fields
            + """
            query School($id: ID!) {
                school(id: $id) {
                    ...schoolFields
                }
            }
        """
        )
        return self.execute(graphql, variables=variables)["school"]

    def test_field_fragment(self) -> None:
        self.authenticated = False
        self.assert_field_fragment_matches_schema(self.school_fields)

    def test_schools(self) -> None:
        schools = self.query_schools()
        assert len(schools) == 6
        assert schools[0]["id"] == "2"
        assert schools[0]["name"] == "Aalto University"
        assert schools[0]["schoolType"] == "University"
        assert schools[0]["city"] == "Espoo"
        assert schools[5]["id"] == "1"
        assert schools[5]["name"] == "University of Turku"
        assert schools[5]["schoolType"] == "University"
        assert schools[5]["city"] == "Turku"

    def test_school(self) -> None:
        school = self.query_school(id=1)
        assert school["id"] == "1"
        assert school["name"] == "University of Turku"

        # ID not found.
        assert self.query_school(id=999) is None
