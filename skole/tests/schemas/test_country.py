from typing import List, cast

from skole.tests.helpers import SkoleSchemaTestCase
from skole.types import ID, JsonDict


class CountrySchemaTests(SkoleSchemaTestCase):

    # language=GraphQL
    country_fields = """
        fragment countryFields on CountryObjectType {
            id
            name
        }
    """

    def query_autocomplete_countries(self) -> List[JsonDict]:
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
        return cast(List[JsonDict], self.execute(graphql))

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
        return self.execute(graphql, variables=variables)

    def test_field_fragment(self) -> None:
        self.authenticated_user = None
        self.assert_field_fragment_matches_schema(self.country_fields)

    def test_autocomplete_countries(self) -> None:
        countries = self.query_autocomplete_countries()
        assert len(countries) == 1
        assert countries[0] == self.query_country(id=1)

    def test_country(self) -> None:
        country = self.query_country(id=1)
        assert country["id"] == "1"
        assert country["name"] == "Finland"
        assert self.query_country(id=999) is None
