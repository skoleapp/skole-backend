from typing import List, cast

from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import ID, JsonDict


class CitySchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    city_fields = """
        fragment cityFields on CityObjectType {
            id
            name
        }
    """

    def query_autocomplete_cities(self) -> List[JsonDict]:
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
        return cast(List[JsonDict], self.execute(graphql))

    def query_city(self, *, id: ID) -> JsonDict:
        variables = {"id": id}

        # language=GraphQL
        graphql = (
            self.city_fields
            + """
            query City($id: ID) {
                city(id: $id) {
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
        assert cities[0] == self.query_city(id=3)
        assert cities[0]["id"] == "3"
        assert cities[0]["name"] == "Espoo"
        assert cities[1]["id"] == "2"
        assert cities[1]["name"] == "Helsinki"

    def test_city(self) -> None:
        city = self.query_city(id=1)
        assert city["id"] == "1"
        assert city["name"] == "Turku"
        assert self.query_city(id=999) is None
