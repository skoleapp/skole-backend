from typing import cast

from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import ID, JsonDict


class SchoolSchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    school_fields = """
        fragment schoolFields on SchoolObjectType {
            id
            name
            commentCount
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

    def query_autocomplete_schools(self, *, name: str = "") -> list[JsonDict]:
        variables = {"name": name}

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
        return cast(list[JsonDict], self.execute(graphql, variables=variables))

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

        assert len(schools) == 6

        # Schools are ordered alphabetically.
        assert schools[0] == self.query_school(id=2)  # Aalto
        assert schools[1] == self.query_school(id=5)  # Metropolia
        assert schools[2] == self.query_school(id=6)  # Raision lukio

        # Query schools by name.
        res = self.query_autocomplete_schools(name="Turku")
        assert len(res) == 2
        assert res[0] == self.query_school(id=4)  # Turku University of Applied Sciences
        assert res[1] == self.query_school(id=1)  # University of Turku

        # No duplicate schools returned (https://trello.com/c/PWAtHaeN).
        res = self.query_autocomplete_schools(name="Aalto")
        assert len(res) == 1

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
        assert len(school["courses"]) == 22
        assert self.query_school(id=999) is None
