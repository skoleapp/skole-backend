from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import JsonDict


class SchoolSchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    school_fields = """
        fragment schoolFields on SchoolObjectType {
            id
            slug
            name
            commentCount
            subjects {
                slug
                name
            }
            courses {
                slug
                name
            }
            schoolType {
                slug
                name
            }
            country {
                slug
                name
            }
            city {
                slug
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
        return self.execute(graphql, variables=variables)

    def query_school(self, *, slug: str) -> JsonDict:
        variables = {"slug": slug}

        # language=GraphQL
        graphql = (
            self.school_fields
            + """
            query School($slug: String) {
                school(slug: $slug) {
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
        assert schools[0] == self.query_school(slug="aalto-university")
        assert schools[1] == self.query_school(
            slug="metropolia-university-of-applied-sciences"
        )
        assert schools[2] == self.query_school(slug="raision-lukio")

        # Query schools by name.
        res = self.query_autocomplete_schools(name="Turku")
        assert len(res) == 2
        assert res[0] == self.query_school(slug="turku-university-of-applied-sciences")
        assert res[1] == self.query_school(slug="university-of-turku")

        # No duplicate schools returned (https://trello.com/c/PWAtHaeN).
        res = self.query_autocomplete_schools(name="Aalto")
        assert len(res) == 1

    def test_school(self) -> None:
        slug = "university-of-turku"
        school = self.query_school(slug=slug)
        assert school["id"] == "1"
        assert school["name"] == "University of Turku"
        assert school["slug"] == slug
        assert school["schoolType"]["slug"] == "university"
        assert school["schoolType"]["name"] == "University"
        assert school["city"]["slug"] == "turku"
        assert school["city"]["name"] == "Turku"
        assert school["country"]["slug"] == "finland"
        assert school["country"]["name"] == "Finland"
        assert len(school["subjects"]) == 2
        assert len(school["courses"]) == 22
        assert self.query_school(slug="no-found") is None
