from graphene.test import Client
from graphene_django.utils.testing import GraphQLTestCase

from api.schemas.schema import schema
from tests.api.utils.school import (
    query_school,
    query_school_type,
    query_school_types,
    query_schools,
)


class SchoolAPITests(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema
    fixtures = ["sample.yaml"]

    def setUp(self) -> None:
        self.client = Client(schema)

    def tearDown(self) -> None:
        del self.client

    def test_query_schools(self) -> None:
        res = query_schools(self)
        assert "errors" not in res
        schools = res["data"]["schools"]
        assert len(schools) == 6
        assert schools[0]["id"] == "2"
        assert schools[0]["name"] == "Aalto University"
        assert schools[0]["schoolType"] == "University"
        assert schools[0]["city"] == "Espoo"
        assert schools[5]["id"] == "1"
        assert schools[5]["name"] == "University of Turku"
        assert schools[5]["schoolType"] == "University"
        assert schools[5]["city"] == "Turku"

    def test_query_school(self) -> None:
        # Test that every School from the list can be queried with its own id.
        res = query_schools(self)
        assert "errors" not in res
        schools = res["data"]["schools"]
        for school in schools:
            assert school == query_school(self, school["id"])["data"]["school"]

        # Test that returns None when ID not found.
        res = query_school(self, 999)
        assert res["data"]["school"] is None

    def test_query_school_types(self) -> None:
        res = query_school_types(self)
        assert "errors" not in res
        school_types = res["data"]["schoolTypes"]
        assert len(school_types) == 3
        assert school_types[0]["id"] == "1"
        assert school_types[0]["name"] == "University"

    def test_query_school_type(self) -> None:
        # Test that every SchoolType from the list can be queried with its own id.
        res = query_school_types(self)
        assert "errors" not in res
        school_types = res["data"]["schoolTypes"]
        for school_type in school_types:
            assert (
                school_type
                == query_school_type(self, school_type["id"])["data"]["schoolType"]
            )

        # Test that returns None when ID not found.
        res = query_school_type(self, 999)
        assert res["data"]["schoolType"] is None
