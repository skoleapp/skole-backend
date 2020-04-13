from typing import List

from mypy.types import JsonDict

from tests.test_utils import SkoleSchemaTestCase


class SchoolTypeSchemaTestCase(SkoleSchemaTestCase):
    authenticated = True

    school_type_fields = """
        fragment schoolTypeFields on SchoolTypeObjectType {
            id
            name
        }
    """

    def query_school_types(self) -> List[JsonDict]:
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

    def query_school_type(self, id: int) -> JsonDict:
        variables = {"id": id}

        graphql = (
            self.school_type_fields
            + """
            query ($id: ID!) {
                schoolType(id: $id) {
                    ...schoolTypeFields
                }
            }
        """
        )
        return self.execute(graphql, variables=variables)["schoolType"]

    def test_school_types(self) -> None:
        school_types = self.query_school_types()
        assert len(school_types) == 3
        assert school_types[0]["id"] == "1"
        assert school_types[0]["name"] == "University"
        assert school_types[1]["id"] == "2"
        assert school_types[1]["name"] == "University of Applied Sciences"

    def test_school_type(self) -> None:
        res = self.query_school_type(id=1)
        assert res["id"] == "1"
        assert res["name"] == "University"

        # ID not found.
        assert self.query_school_type(id=999) is None
