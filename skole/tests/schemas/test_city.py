from typing import List

from mypy.types import JsonDict

from skole.tests.helpers import SkoleSchemaTestCase
from skole.utils.types import ID


class CitySchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    city_fields = """
        fragment cityFields on CityObjectType {
            id
            name
        }
    """

    def query_cities(self) -> List[JsonDict]:
        # language=GraphQL
        graphql = (
            self.city_fields
            + """
            query Cities {
                cities {
                    ...cityFields
                }
            }
            """
        )
        return self.execute(graphql)["cities"]

    def query_city(self, *, id: ID) -> JsonDict:
        variables = {"id": id}

        # language=GraphQL
        graphql = (
            self.city_fields
            + """
            query City($id: ID!) {
                city(id: $id) {
                    ...cityFields
                }
            }
            """
        )
        return self.execute(graphql, variables=variables)["city"]

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.city_fields)

    def test_cities(self) -> None:
        cities = self.query_cities()
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
