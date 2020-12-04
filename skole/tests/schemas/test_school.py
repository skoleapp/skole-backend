from typing import List, cast

from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import ID, JsonDict


class SchoolSchemaTests(SkoleSchemaTestCase):

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

    def query_autocomplete_schools(self, name: str = "") -> List[JsonDict]:
        # language=GraphQL
        graphql = (
            self.school_fields
            + """
            query AutocompleteSchools($name: String) {
                autocompleteSchools(name: $name) {
                    ...schoolFields
                }
            }
            """
        )
        return cast(List[JsonDict], self.execute(graphql))

    def query_school(self, *, id: ID) -> JsonDict:
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
        return self.execute(graphql, variables=variables)

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.school_fields)

    def test_autocomplete_schools(self) -> None:
        schools = self.query_autocomplete_schools()

        # By default, schools are ordered by the amount of courses.
        assert schools[0] == self.query_school(id=1)  # Most courses.
        assert schools[1] == self.query_school(id=2)  # 2nd most courses.
        assert schools[2] == self.query_school(id=3)  # 3rd most courses.

        # Query schools by name.
        res = self.query_autocomplete_schools("Turku")
        assert len(res) == 6
        assert res[0] == self.query_school(id=1)  # University of Turku.
        assert res[2] == self.query_school(
            id=3
        )  # Turku University of Applied Sciences.

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
        assert len(school["subjects"]) == 2
        assert len(school["courses"]) == 12
        assert self.query_school(id=999) is None
