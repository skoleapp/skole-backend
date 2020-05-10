from typing import List

from mypy.types import JsonDict

from skole.tests.utils import SchemaTestCase


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
            schoolType {
                id
                name
            }
            country {
                id
                name
            }
            city {
                id
                name
            }
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

    def test_school(self) -> None:
        school = self.query_school(id=1)
        assert school["id"] == "1"
        assert school["name"] == "University of Turku"
        assert school["schoolType"]["id"] == "1"
        assert school["schoolType"]["name"] == "University"
        assert school["city"]["id"] == "1"
        assert school["city"]["name"] == "Turku"
        assert school["country"]["id"] == "1"
        assert school["country"]["name"] == "Finland"
        assert len(school["subjects"]) == 1
        assert len(school["courses"]) == 12

        # ID not found.
        assert self.query_school(id=999) is None
