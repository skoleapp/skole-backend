import json
from typing import Any

from django.http import HttpResponse
from graphene_django.utils.testing import GraphQLTestCase
from mypy.types import JsonDict

from api.schemas.schema import schema


class SchemaTestCase(GraphQLTestCase):
    """This class should be subclassed for every schema test case.
    Users of this class should explicitly set the `authenticated` attribute
    to suit that test case's needs.
    """

    GRAPHQL_SCHEMA = schema
    fixtures = ["test-data.yaml"]

    # This should be set at the class level, but it can still be overridden
    # for individual tests when needed.
    authenticated: bool

    def execute(
        self, graphql: str, should_error: bool = False, **kwargs: Any
    ) -> JsonDict:
        """Run a GraphQL query assert that status code was 200 (=syntax was ok)
        and that the result didn't have an "error" section

        Args:
            graphql: The query that will be executed
            should_error: True if an error is to be expected, then we also return it.
            **kwargs: `header` kwarg will get merged with the possible token header.
                Other kwargs are passed straight to GraphQLTestCase.query().

        Returns:
            The resulting JSON "data" section if `should_error` is False.
            Otherwise returns both the "error" and "data" sections.
        """

        # Token is for testuser2, hardcoded since always getting a fresh one with
        # a login mutation takes time and slows down the tests.
        if self.authenticated:
            token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InRlc3R1c2VyMiIsImV4cCI6MTU4NzMwNDgyMCwib3JpZ0lhdCI6MTU4NjcwMDAyMH0.1ikCSgWk2Giic-dyn0ZUa30aXMpd8b7jSUbYfze9oFA"
            headers = {"HTTP_AUTHORIZATION": f"JWT {token}"}
        else:
            headers = {}

        headers.update(kwargs.pop("headers", {}))

        response = self.query(graphql, **kwargs, headers=headers)

        if should_error:
            self.assertResponseHasErrors(response)
            return json.loads(response.content)
        else:
            self.assertResponseNoErrors(response)
            return json.loads(response.content)["data"]

    def execute_input_mutation(
        self,
        /,
        input_type: str,
        op_name: str,
        input: JsonDict,
        result: str,
        fragment: str = "",
    ) -> JsonDict:
        """Shortcut for running a mutation which takes only an input argument.

        Args:
            input_type: Name of the GraphQL input type object.
            op_name: Name of the mutation.
            input: The arguments going into the input argument of the mutation.
            result: GraphQL snippet of the fields which want to be queried from the result.
            fragment: Extra GraphQL snippet which will be inserted before the mutation query.
                Useful for providing a GraphQL fragment which can then used in result.

        Returns:
            The resulting JSON "data" section.
        """

        graphql = (
            fragment
            + f"""
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
        )
        return self.execute(graphql, input_data=input, op_name=op_name)[op_name]

    def assertResponseNoErrors(self, resp: HttpResponse) -> None:
        """Overridden and re-ordered to immediately see the errors if there were any."""
        content = json.loads(resp.content)
        self.assertNotIn("errors", content)
        self.assertEqual(resp.status_code, 200)
