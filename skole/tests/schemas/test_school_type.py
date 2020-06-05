from typing import List

from mypy.types import JsonDict

from skole.tests.helpers import SkoleSchemaTestCase
from skole.utils.types import ID


class SchoolTypeSchemaTests(SkoleSchemaTestCase):
    authenticated = True

    # language=GraphQL
    school_type_fields = """
        fragment schoolTypeFields on SchoolTypeObjectType {
            id
            name
        }
    """

    def query_school_types(self) -> List[JsonDict]:
        # language=GraphQL
        graphql = (
            self.school_type_fields
            + """
            query SchoolTypes {
                schoolTypes {
                    ...schoolTypeFields
                }
            }
            """
        )
        return self.execute(graphql)["schoolTypes"]

    def query_school_type(self, id: ID) -> JsonDict:
        variables = {"id": id}

        # language=GraphQL
        graphql = (
            self.school_type_fields
            + """
            query SchoolType($id: ID!) {
                schoolType(id: $id) {
                    ...schoolTypeFields
                }
            }
            """
        )
        return self.execute(graphql, variables=variables)["schoolType"]

    def test_field_fragment(self) -> None:
        self.authenticated = False
        self.assert_field_fragment_matches_schema(self.school_type_fields)

    def test_school_types(self) -> None:
        school_types = self.query_school_types()
        assert len(school_types) == 3
        # SchoolTypes should be ordered by IDs.
        assert school_types[0] == self.query_school_type(id=1)
        assert school_types[0]["id"] == "1"
        assert school_types[0]["name"] == "University"
        assert school_types[1]["id"] == "2"
        assert school_types[1]["name"] == "University of Applied Sciences"

    def test_school_type(self) -> None:
        res = self.query_school_type(id=1)
        assert res["id"] == "1"
        assert res["name"] == "University"

        assert self.query_school_type(id=999) is None
