import json
from typing import Any

from graphene_django.utils.testing import GraphQLTestCase
from mypy.types import JsonDict

from api.schemas.schema import schema


class BaseSchemaTestCase(GraphQLTestCase):
    """This class should be subclassed for every schema test.
    Users of this class should explicitly set the `authenticated` attribute
    to suit that test case's needs.
    """

    GRAPHQL_SCHEMA = schema
    fixtures = ["test-data.yaml"]

    # This should be set at the class level, but it can still be overridden
    # for individual tests when needed.
    authenticated: bool

    def execute(self, graphql: str, *args: Any, **kwargs: Any) -> JsonDict:
        """Run a GraphQL query and return the resulting JSON "data" section."""

        # Token is for testuser2, hardcoded since always getting a fresh one with
        # a login mutation takes time and slows down the tests.
        if self.authenticated:
            token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyMiIsImV4cCI6MTU4NzMwNDgyMCwib3JpZ0lhdCI6MTU4NjcwMDAyMH0.1ikCSgWk2Giic-dyn0ZUa30aXMpd8b7jSUbYfze9oFA"
            headers = {"HTTP_AUTHORIZATION": f"JWT {token}"}
        else:
            headers = {}

        if "headers" in kwargs:
            headers.update(kwargs["headers"])

        response = self.query(graphql, *args, **kwargs, headers=headers)

        self.assertResponseNoErrors(response)
        return json.loads(response.content)["data"]


def execute_input_mutation(
    test_case: BaseSchemaTestCase,
    input_type: str,
    op_name: str,
    input: JsonDict,
    result: str,
) -> JsonDict:

    mutation = f"""
      mutation ($input: {input_type}) {{
        {op_name}(input: $input) {{
          errors {{
            field
            messages
          }}
          {result}
        }}
      }}
    """
    return test_case.execute(mutation, variables={"input": input}, op_name=op_name)[
        op_name
    ]
