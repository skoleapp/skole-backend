"""Module for testing compatibility of value/overridden 3rd party code."""
import importlib

import graphql.execution.utils
from graphene_django.utils import GraphQLTestCase
from graphene_django.views import GraphQLView

from skole.tests.helpers import checksum

# Theses tests that make sure that we immediately notice if the source code
# of the functions we have overridden or monkey value has changed,
# so that we can always ensure full compatibility.
#
# If any of these tests fail, it's not the end of the world, one just needs to check
# the releases of that package and see what has changed in the code. After verifying
# that the change didn't affect our usage, or after altering our overridden code, the
# checksum in the assertion can be changed to correspond to the new 3rd party code.


def test_report_error_code_has_not_changed() -> None:
    importlib.reload(graphql.execution.utils)
    assert (
        checksum(graphql.execution.utils.ExecutionContext.report_error)
        == "fa7cdbca837c4ebfd294"
    )


def test_graphql_view_code_has_not_changed() -> None:
    assert checksum(GraphQLView.parse_body) == "b6d13668aa8a9c22e9a2"


def test_graphql_test_case_code_has_not_changed() -> None:
    assert checksum(GraphQLTestCase) == "6e3548dd471f0a213673"
