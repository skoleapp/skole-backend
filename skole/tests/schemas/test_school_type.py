from typing import cast

from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import JsonDict


class SchoolTypeSchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    school_type_fields = """
        fragment schoolTypeFields on SchoolTypeObjectType {
            slug
            name
        }
    """

    def query_autocomplete_school_types(self) -> list[JsonDict]:
        # language=GraphQL
        graphql = (
            self.school_type_fields
            + """
            query AutocompleteSchoolTypes {
                autocompleteSchoolTypes {
                    ...schoolTypeFields
                }
            }
            """
        )
        return cast(list[JsonDict], self.execute(graphql))

    def query_school_type(self, *, slug: str) -> JsonDict:
        variables = {"slug": slug}

        # language=GraphQL
        graphql = (
            self.school_type_fields
            + """
            query SchoolType($slug: String) {
                schoolType(slug: $slug) {
                    ...schoolTypeFields
                }
            }
            """
        )

        return self.execute(graphql, variables=variables)

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.school_type_fields)

    def test_autocomplete_school_types(self) -> None:
        school_types = self.query_autocomplete_school_types()
        assert len(school_types) == 3
        # SchoolTypes should be ordered by IDs.
        assert school_types[0]["slug"] == "university"
        assert school_types[0]["name"] == "University"
        assert school_types[1]["slug"] == "university-of-applied-sciences"
        assert school_types[1]["name"] == "University of Applied Sciences"

    def test_school_type(self) -> None:
        slug = "university"
        res = self.query_school_type(slug=slug)
        assert res["slug"] == slug
        assert res["name"] == "University"
        assert self.query_school_type(slug="not-found") is None
