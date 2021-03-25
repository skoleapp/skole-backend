from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import JsonDict, JsonList


class CitySchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    city_fields = """
        fragment cityFields on CityObjectType {
            slug
            name
        }
    """

    def query_autocomplete_cities(self) -> JsonList:
        # language=GraphQL
        graphql = (
            self.city_fields
            + """
            query AutocompleteCities {
                autocompleteCities {
                    ...cityFields
                }
            }
            """
        )
        return self.execute(graphql)

    def query_city(self, *, slug: str) -> JsonDict:
        variables = {"slug": slug}

        # language=GraphQL
        graphql = (
            self.city_fields
            + """
            query City($slug: String) {
                city(slug: $slug) {
                    ...cityFields
                }
            }
            """
        )

        return self.execute(graphql, variables=variables)

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.city_fields)

    def test_autocomplete_cities(self) -> None:
        cities = self.query_autocomplete_cities()
        assert len(cities) == 5
        # Cities should be ordered alphabetically.
        assert cities[0]["slug"] == "espoo"
        assert cities[0]["name"] == "Espoo"
        assert cities[1]["slug"] == "helsinki"
        assert cities[1]["name"] == "Helsinki"

    def test_city(self) -> None:
        slug = "turku"
        city = self.query_city(slug=slug)
        assert city["slug"] == slug
        assert city["name"] == "Turku"
        assert self.query_city(slug="not-found") is None
