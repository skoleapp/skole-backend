import json
from typing import Any, Optional, Sequence, Tuple, Union

from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse
from graphene_django.utils.testing import GraphQLTestCase
from mypy.types import JsonDict

from skole.schema import schema


class SkoleSchemaTestCase(GraphQLTestCase):
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
                Other kwargs are passed straight to self.query().

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

        # Ignore: Mypy thinks its getting multiple values for `headers`, but they are
        #   popped from the `kwargs`.
        response = self.query(graphql, **kwargs, headers=headers)  # type: ignore[misc]

        if self.should_error:
            self.assertResponseHasErrors(response)
            return json.loads(response.content)
        else:
            self.assertResponseNoErrors(response)
            return json.loads(response.content)["data"]

    def execute_input_mutation(
        self,
        *,
        input_type: str,
        op_name: str,
        input: JsonDict,
        result: str,
        fragment: str = "",
        file_data: Optional[Sequence[Tuple[str, UploadedFile]]] = None,
    ) -> JsonDict:
        """Shortcut for running a mutation which takes only an input argument.

        Args:
            input_type: Name of the GraphQL input type object.
            op_name: Name of the mutation.
            input: The arguments going into the input argument of the mutation.
            result: GraphQL snippet of the fields which want to be queried from the result.
            fragment: Extra GraphQL snippet which will be inserted before the mutation query.
                Useful for providing a GraphQL fragment which can then used in `result.`
            file_data: Files to the mutation as a sequence of (field_name, file) pairs.
                By passing these the self.query() will automatically use the correct
                multipart/form-data content-type. It will also automatically handle all
                of the inserting of the files into the request body.

        Returns:
            The resulting JSON "data".op_name section if `should_error` is False.
            Otherwise returns both the "error" and "data" sections.
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
        res = self.execute(
            graphql, input_data=input, op_name=op_name, file_data=file_data
        )
        if self.should_error:
            return res
        return res[op_name]  # Convenience to get straight to the result object.

    def query(
        self,
        query: str,
        op_name: Optional[str] = None,
        input_data: Optional[JsonDict] = None,
        variables: Optional[JsonDict] = None,
        headers: Optional[JsonDict] = None,
        file_data: Optional[Sequence[Tuple[str, UploadedFile]]] = None,
    ) -> HttpResponse:
        """Overridden to allow uploading files with a multipart/form-data POST.

        See parent's docstring for more info.
        """
        body: JsonDict = {"query": query}
        if op_name:
            body["operation_name"] = op_name
        if variables:
            body["variables"] = variables
        if input_data:
            if variables in body:
                body["variables"]["input"] = input_data
            else:
                body["variables"] = {"input": input_data}

        extra = headers or {}

        if file_data:
            # This imitates the way Apollo Client places handles files in a GraphQL query.
            variable_map = {}
            file_dict = {}
            for i, (field, file) in enumerate(file_data, start=1):
                variable_map[str(i)] = [f"variables.input.{field}"]
                file_dict[str(i)] = file

            data: Union[JsonDict, str] = {
                "operations": json.dumps(body),
                "map": json.dumps(variable_map),
                **file_dict,
            }

        else:
            data = json.dumps(body)
            extra.update({"content_type": "application/json"})

        return self._client.post(path=self.GRAPHQL_URL, data=data, **extra)

    def assertResponseNoErrors(self, resp: HttpResponse) -> None:
        """Overridden and re-ordered to immediately see the errors if there were any.

        See parent's docstring for more info.
        """
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
