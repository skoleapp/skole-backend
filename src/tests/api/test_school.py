from graphene.test import Client
from graphene_django.utils.testing import GraphQLTestCase

from api.schemas.schema import schema
from tests.api.utils.school import (
    create_sample_school,
    query_school,
    query_school_list,
)


class SchoolAPITests(GraphQLTestCase):
    GRAPHQL_SCHEMA = schema

    def setUp(self) -> None:
        self.school1 = create_sample_school(name="Test School 1")
        self.school2 = create_sample_school(name="Test School 2")
        self.school3 = create_sample_school(name="Test School 3")
        self.client = Client(schema)

    def tearDown(self) -> None:
        self.school1.delete()
        self.school2.delete()
        self.school3.delete()
        del self.client

    def test_school_list(self) -> None:
        res = query_school_list(self)
        cont = res["data"]["schoolList"]
        assert len(cont) == 3
        assert cont[0]["name"] == self.school1.name
        assert cont[1]["name"] == self.school2.name
        assert cont[2]["name"] == self.school3.name

    def test_school_detail(self) -> None:
        res = query_school(self, self.school1.id)
        cont = res["data"]["school"]
        assert cont["id"] == str(self.school1.id)
        assert cont["name"] == self.school1.name

        # ID not found
        res = query_school(self, 999)
        cont = res["data"]["school"]
        assert cont is None
        assert "does not exist" in res["errors"][0]["message"]
