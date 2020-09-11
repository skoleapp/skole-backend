import datetime
import hashlib
import inspect
import json
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional, Sequence, Tuple, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.http import HttpResponse
from django.test import TestCase
from graphql_jwt.settings import jwt_settings
from graphql_jwt.shortcuts import get_token
from graphql_jwt.utils import delete_cookie

from skole.types import ID, JsonDict

FileData = Optional[Sequence[Tuple[str, File]]]


class SkoleSchemaTestCase(TestCase):
    """Base class for all schema tests.

    Heavily inspired by `graphene_utils.testing.GraphQLTestCase`.

    Attributes:
        authenticated_user: When set to an ID, a JWT token made for the
            user with this pk is sent with all the requests.
    """

    fixtures = ["test-data.yaml"]

    authenticated_user: ID = None

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
        through `self.execute` or `self.execute_input_mutation` etc.

        Args:
            query: GraphQL query to run.
            op_name: If the query is a mutation or named query, you must
                supply the op_name.  For anon queries ("{ ... }"),
                should be None (default).
            input_data: If provided, the $input variable in GraphQL will be set
                to this value. If both ``input_data`` and ``variables``,
                are provided, the ``input`` field in the ``variables``
                dict will be overwritten with this value.
            variables: If provided, the "variables" field in GraphQL will be
                set to this value.
            headers: If provided, the headers in POST request to GRAPHQL_URL
                will be set to this value.
            file_data: Files to the mutation as a sequence of (field_name, file) pairs.
                By passing these the self.query() will automatically use the correct
                multipart/form-data content-type. It will also automatically handle all
                of the inserting of the files into the request body.

        Returns:
            Response object from the client.
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

        return self.client.post(path="/graphql/", data=data, **extra)

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
                Other kwargs are passed straight to self.query, see also its docstring.

        Returns:
            The resulting JSON data.name section if `assert_error` is False.
            Otherwise returns both the "error" and "data" sections.

            Note: The return value is type hinted for simplicity to be a `JsonDict`,
            but it can actually be `List[JsonDict]` in cases when we're fetching a list
            of objects. In those cases we'll do a `cast()` before accessing the data.
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

        if not self.authenticated_user:
            delete_cookie(response, jwt_settings.JWT_COOKIE_NAME)

        if assert_error:
            self._assert_response_has_errors(response)
            return json.loads(response.content)
        else:
            self._assert_response_no_errors(response)
            data = json.loads(response.content)["data"]
            assert len(data) == 1, "This method only returns data from the first key."
            return data.popitem()[1]

    def execute_input_mutation(
        self,
        *,
        name: str,
        input_type: str,
        input: JsonDict,
        result: str,
        fragment: str = "",
        file_data: FileData = None,
        assert_error: bool = False,
    ) -> JsonDict:
        """Shortcut for running a mutation which takes only an input argument.

        Args:
            input_type: Name of the GraphQL input type object.
            name: Name of the mutation in the schema.
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
            The resulting JSON data.name section if `assert_error` is False.
            Otherwise returns both the "error" and "data" sections.
        """
        graphql = (
            fragment
            + f"""
            mutation ($input: {input_type}) {{
                {name}(input: $input) {{
                    errors {{
                        field
                        messages
                    }}
                    {result}
                }}
            }}
            """
        )
        return self.execute(
            graphql=graphql,
            input_data=input,
            file_data=file_data,
            assert_error=assert_error,
        )

    def execute_non_input_mutation(
        self, *, name: str, result: str, fragment: str = "", assert_error: bool = False,
    ) -> JsonDict:
        """Shortcut for running a mutation which takes no input as an argument.

        Args:
            name: Name of the mutation in the schema.
            result: GraphQL snippet of the fields which want to be queried from the result.
            fragment: Extra GraphQL snippet which will be inserted before the mutation query.
                Useful for providing a GraphQL fragment which can then used in `result.`
            assert_error: Whether the result should contain a top level "errors" section.
                Form mutation errors never have this.

        Returns:
            The resulting JSON data.name section if `assert_error` is False.
            Otherwise returns both the "error" and "data" sections.
        """

        graphql = (
            fragment
            + f"""
            mutation {{
                {name} {{
                    errors {{
                        field
                        messages
                    }}
                    {result}
                }}
            }}
            """
        )
        return self.execute(graphql=graphql, op_name=name, assert_error=assert_error)

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

        for field in res["fields"]:
            self.assertIn(field["name"], field_fragment)

    def _assert_response_no_errors(self, response: HttpResponse) -> None:
        content = json.loads(response.content)
        self.assertNotIn("errors", content)
        assert response.status_code == 200

    def _assert_response_has_errors(self, response: HttpResponse) -> None:
        content = json.loads(response.content)
        self.assertIn("errors", content)
        if "data" in content:
            # If there is a "data" section it should only have keys with empty values.
            for key, value in content["data"].items():
                assert isinstance(key, str)
                assert value is None


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


def is_slug_match(file_path: str, url_with_slug: str) -> bool:
    """Return True if the two paths match each other with an optional slug.

    The paths will still match even if one of them is a relative path, and the other
    is an absolute one (no prexix slash).

    Examples:
        >>> is_slug_match("/media/test/foo.jpg", "/media/test/fooXfa123.jpg")
        True
        >>> is_slug_match("/media/test/foo.jpg", "/media/test/foo.jpg")
        True
        >>> is_slug_match("media/test/foo.jpg", "/media/test/foo.jpg")
        True
        >>> is_slug_match("/media/test/foo.jpg", "/media/test/foo-bar.jpg")
        False
        >>> is_slug_match("/media/test/foo.jpg", "/foo.jpg")
        False
    """
    # Can use Python 3.9's `str.removeprefix`.
    if file_path.startswith("/"):
        file_path = file_path[1:]
    path, extension = file_path.rsplit(".", 1)
    return bool(re.match(fr"^/{path}\w*\.{extension}$", url_with_slug))


def checksum(obj: Any) -> str:
    """Return a stable 10 digit hex checksum for the given object.

    Useful for testing if a source code of the object has changed.
    """
    return hashlib.shake_256(inspect.getsource(obj).encode()).hexdigest(10)


@contextmanager
def open_as_file(path: Union[str, Path]) -> Generator[File, None, None]:
    """Use as a contextmanager to open the file in the given path as a Django File."""
    if not isinstance(path, Path):
        path = Path(path)

    with open(settings.BASE_DIR / path, "rb") as f:
        yield File(f)
