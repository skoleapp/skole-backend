import json
from typing import Any

from django.http import HttpResponse
from graphene_django.utils.testing import GraphQLTestCase
from mypy.types import JsonDict

from skole.schema import schema


class SchemaTestCase(GraphQLTestCase):
    """Base class for all schema tests.

    Attributes:
        authenticated: When True a JWT token is sent with all the requests.
        should_error: Can be set to True for individual tests, for making
            that test pass when the request errors.
    """

    GRAPHQL_SCHEMA = schema
    fixtures = ["test-data.yaml"]

    authenticated: bool = False
    should_error: bool = False

    def execute(self, graphql: str, **kwargs: Any) -> JsonDict:
        """Run a GraphQL query, if `should_error` attribute is False assert that status
        code was 200 (=syntax was ok) and that the result didn't have "error" section.
        If `should_error` is True, we assert that the result does contain "error".

        Args:
            graphql: The query that will be executed
            **kwargs: `header` kwarg will get merged with the possible token header.
                Other kwargs are passed straight to GraphQLTestCase.query().

        Returns:
            The resulting JSON "data" section if `should_error` is False.
            Otherwise returns both the "error" and "data" sections.
        """

        # Token is for testuser2, hardcoded since always getting a fresh one with
        # a login mutation takes time and slows down the tests.
        if self.authenticated:
            token = (
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6In"
                "Rlc3R1c2VyMiIsImV4cCI6MTU4NzMwNDgyMCwib3JpZ0lhdCI6MTU4N"
                "jcwMDAyMH0.1ikCSgWk2Giic-dyn0ZUa30aXMpd8b7jSUbYfze9oFA"
            )
            headers = {"HTTP_AUTHORIZATION": f"JWT {token}"}
        else:
            headers = {}

        headers.update(kwargs.pop("headers", {}))

        response = self.query(graphql, **kwargs, headers=headers)

        if self.should_error:
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
        res = self.execute(graphql, input_data=input, op_name=op_name)
        if self.should_error:
            return res
        return res[op_name]  # Convenience to get straight to the object.

    def assertResponseNoErrors(self, resp: HttpResponse) -> None:
        """Overridden and re-ordered to immediately see the errors if there were any."""
        content = json.loads(resp.content)
        self.assertNotIn("errors", content)
        self.assertEqual(resp.status_code, 200)

    def assert_field_fragment_matches_schema(self, field_fragment: str) -> None:
        """Assert that the given fragment contains all the fields that are actually
        queryable on that object type its defined for."""
        # language=GraphQL
        graphql = """
            query IntrospectAllFields($name: String!) {
                __type(name: $name) {
                    fields {
                        name
                    }
                }
            }
        """
        object_type = field_fragment.split()[3]
        res = self.execute(graphql, variables={"name": object_type})

        for field in res["__type"]["fields"]:
            assert field["name"] in field_fragment
