import datetime
import json
from typing import Any, Optional, Sequence, Tuple, Union

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse
from graphene_django.utils import GraphQLTestCase
from graphql_jwt.shortcuts import get_token
from mypy.types import JsonDict

from skole.schema import schema

FileData = Optional[Sequence[Tuple[str, UploadedFile]]]


class SkoleSchemaTestCase(GraphQLTestCase):
    """Base class for all schema tests.

    Attributes:
        authenticated_user: When set to a integer, a JWT token made for the
            user with this pk is sent with all the requests.
    """

    fixtures = ["test-data.yaml"]
    GRAPHQL_SCHEMA = schema

    authenticated_user: Optional[int] = None

    def query(
        self,
        query: str,
        op_name: Optional[str] = None,
        input_data: Optional[JsonDict] = None,
        variables: Optional[JsonDict] = None,
        headers: Optional[JsonDict] = None,
        file_data: FileData = None,
    ) -> HttpResponse:
        """Overridden to allow uploading files with a multipart/form-data POST.

        This should probably not be used on its own, but instead should be called
        through `self.execute` or `self.execute_input_mutation`. See also parent's
        docstring for more info.
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
            # This imitates the way Apollo Client places files in a GraphQL query.
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

    def execute(
        self, graphql: str, *, assert_error: bool = False, **kwargs: Any
    ) -> JsonDict:
        """Run a GraphQL query, if `assert_error` parameter is False assert that status
        code was 200 (=syntax was ok) and that the result didn't have "error" section.
        If `assert_error` is True, we assert that the result does contain "error".

        Args:
            graphql: The query that will be executed.
            assert_error: Can be set to True for making that execution pass when
                the request fails and the response has a top level "errors" section.
                Note that when form mutations error out, they don't have this section.
            **kwargs: `header` kwarg will get merged with the possible token header.
                Other kwargs are passed straight to self.query().

        Returns:
            The resulting JSON "data" section if `assert_error` is False.
            Otherwise returns both the "error" and "data" sections.
        """

        if self.authenticated_user:
            token = get_token(get_user_model().objects.get(pk=self.authenticated_user))
            headers = {"HTTP_AUTHORIZATION": f"JWT {token}"}
        else:
            headers = {}

        headers.update(kwargs.pop("headers", {}))

        # Ignore: Mypy thinks its getting multiple values for `headers`, but they are
        #   popped from the `kwargs`.
        response = self.query(graphql, **kwargs, headers=headers)  # type: ignore[misc]

        if assert_error:
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
        file_data: FileData = None,
        assert_error: bool = False,
    ) -> JsonDict:
        """Shortcut for running a mutation which takes only an input argument.

        Args:
            input_type: Name of the GraphQL input type object.
            op_name: Name of the mutation in the schema.
            input: The arguments going into the input argument of the mutation.
            result: GraphQL snippet of the fields which want to be queried from the result.
            fragment: Extra GraphQL snippet which will be inserted before the mutation query.
                Useful for providing a GraphQL fragment which can then used in `result.`
            file_data: Files to the mutation as a sequence of (field_name, file) pairs.
                By passing these the self.query() will automatically use the correct
                multipart/form-data content-type. It will also automatically handle all
                of the inserting of the files into the request body.
            assert_error: Whether the result should contain a top level "errors" section.
                Form mutation errors never have this.

        Returns:
            The resulting JSON "data".op_name section if `assert_error` is False.
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
            graphql=graphql,
            input_data=input,
            op_name=op_name,
            file_data=file_data,
            assert_error=assert_error,
        )
        if assert_error:
            return res
        return res[op_name]  # Convenience to get straight to the result object.

    def assertResponseNoErrors(self, resp: HttpResponse) -> None:
        """Overridden and re-ordered to immediately see the errors if there were any.

        See parent's docstring for more info.
        """
        content = json.loads(resp.content)
        self.assertNotIn("errors", content)
        self.assertEqual(resp.status_code, 200)

    def assertResponseHasErrors(self, resp: HttpResponse) -> None:
        """Overridden to do more thorough checking.

        See parent's docstring for more info.
        """
        content = json.loads(resp.content)
        self.assertIn("errors", content)
        if "data" in content:
            # If there is a "data" section it should have only keys with empty values.
            for key, value in content["data"].items():
                assert isinstance(key, str)
                assert value is None

    def assert_field_fragment_matches_schema(self, field_fragment: str, /) -> None:
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
            self.assertIn(field["name"], field_fragment)


def get_form_error(res: JsonDict, /) -> str:
    """Return the first error message from a result containing a form mutation error."""
    try:
        return res["errors"][0]["messages"][0]
    except (KeyError, TypeError):
        assert False, f"`res` didn't contain a form mutation error: \n{res}"


def get_graphql_error(res: JsonDict, /) -> str:
    """Return the first error message from a result containing a GraphQL error."""
    try:
        return res["errors"][0]["message"]
    except (KeyError, TypeError):
        assert False, f"`res` didn't contain a GraphQL error: \n{res}"


def is_iso_datetime(datetime_string: str, /) -> bool:
    """Return True if the given string is a valid ISO-format datetime, otherwise False.

    Examples:
        >>> is_iso_datetime("2020-01-01T12:00:00+00:00")
        True
        >>> is_iso_datetime("2020-01-01")
        False
        >>> is_iso_datetime("T12:00:00+00:00")
        False
        >>> is_iso_datetime("foobar")
        False
    """
    try:
        datetime.datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        return False
    else:
        return True
