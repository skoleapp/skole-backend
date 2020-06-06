from typing import List

from mypy.types import JsonDict

from skole.tests.helpers import SkoleSchemaTestCase
from skole.utils.types import ID


class CountrySchemaTests(SkoleSchemaTestCase):
    authenticated = True

    # language=GraphQL
    country_fields = """
        fragment countryFields on CountryObjectType {
            id
            name
        }
    """

    def query_countries(self) -> List[JsonDict]:
        # language=GraphQL
        graphql = (
            self.country_fields
            + """
            query Countries {
                countries {
                    ...countryFields
                }
            }
            """
        )
        return self.execute(graphql)["countries"]

    def query_country(self, *, id: ID) -> JsonDict:
        variables = {"id": id}

        # language=GraphQL
        graphql = (
            self.country_fields
            + """
            query Country($id: ID!) {
                country(id: $id) {
                    ...countryFields
                }
            }
            """
        )
        return self.execute(graphql, variables=variables)["country"]

    def test_field_fragment(self) -> None:
        self.authenticated = False
        self.assert_field_fragment_matches_schema(self.country_fields)

    def test_countries(self) -> None:
        countries = self.query_countries()
        assert len(countries) == 1
        assert countries[0] == self.query_country(id=1)

    def test_country(self) -> None:
        country = self.query_country(id=1)
        assert country["id"] == "1"
        assert country["name"] == "Finland"

        assert self.query_country(id=999) is None
