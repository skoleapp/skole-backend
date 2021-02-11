from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import JsonDict


class CountrySchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    country_fields = """
        fragment countryFields on CountryObjectType {
            slug
            name
        }
    """

    def query_autocomplete_countries(self) -> list[JsonDict]:
        # language=GraphQL
        graphql = (
            self.country_fields
            + """
            query AutocompleteCountries {
                autocompleteCountries {
                    ...countryFields
                }
            }
            """
        )
        return self.execute(graphql)

    def query_country(self, *, slug: str) -> JsonDict:
        variables = {"slug": slug}

        # language=GraphQL
        graphql = (
            self.country_fields
            + """
            query Country($slug: String) {
                country(slug: $slug) {
                    ...countryFields
                }
            }
            """
        )
        return self.execute(graphql, variables=variables)

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.country_fields)

    def test_autocomplete_countries(self) -> None:
        countries = self.query_autocomplete_countries()
        assert len(countries) == 1
        assert countries[0] == self.query_country(slug="finland")

    def test_country(self) -> None:
        slug = "finland"
        country = self.query_country(slug=slug)
        assert country["slug"] == slug
        assert country["name"] == "Finland"
        assert self.query_country(slug="not-found") is None
