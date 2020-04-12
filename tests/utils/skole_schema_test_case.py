import json
from typing import Any

from graphene_django.utils.testing import GraphQLTestCase
from mypy.types import JsonDict

from api.schemas.schema import schema


class SkoleSchemaTestCase(GraphQLTestCase):
    """This class should be subclassed for every schema test.
    Users of this class should explicitly set `authenticated` attribute
    to suit that test's needs.
    """

    GRAPHQL_SCHEMA = schema
    fixtures = ["test-data.yaml"]
    authenticated: bool  # Users of this class have to explicitly set this.

    def execute(self, query: str, *args: Any, **kwargs: Any) -> JsonDict:
        """Helper method for running a GraphQL query and getting it's json response."""

        # Token is for testuser2, hardcoded since always getting a fresh one with
        # a login mutation takes time and slows down the tests.
        if self.authenticated:
            token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyMiIsImV4cCI6MTU4NzMwNDgyMCwib3JpZ0lhdCI6MTU4NjcwMDAyMH0.1ikCSgWk2Giic-dyn0ZUa30aXMpd8b7jSUbYfze9oFA"
            headers = {"HTTP_AUTHORIZATION": f"JWT {token}"}
        else:
            headers = {}

        if "headers" in kwargs:
            headers = {**headers, **kwargs.pop("headers")}

        response = self.query(query, *args, **kwargs, headers=headers)

        # Only on GraphQL syntax errors we get status != 200.
        self.assertResponseNoErrors(response)
        return json.loads(response.content)["data"]
