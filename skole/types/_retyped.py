"""This module contains retyped versions of third party code."""
from __future__ import annotations

from typing import List, Optional, Union

from django.http import HttpRequest
from graphql.language.ast import Field, OperationDefinition
from graphql.type.definition import GraphQLList, GraphQLObjectType, GraphQLScalarType
from graphql.type.schema import GraphQLSchema

from ._aliases import JsonDict


class ResolveInfo:  # pylint: disable=too-many-instance-attributes
    """
    Retyped version of `graphql.ResolveInfo`.

    The main reason for this is to specify `context` to be a `HttpRequest`,
    like it in practice always is.

    This should be used everywhere in place of the original `graphql.ResolveInfo`
    as the type of a resolver's `info` parameter.
    """

    __slots__ = (
        "field_name",
        "field_asts",
        "return_type",
        "parent_type",
        "schema",
        "fragments",
        "root_value",
        "operation",
        "variable_values",
        "context",
        "path",
    )

    def __init__(
        self,
        field_name: str,
        field_asts: List[Field],
        return_type: Union[GraphQLList, GraphQLObjectType, GraphQLScalarType],
        parent_type: GraphQLObjectType,
        schema: GraphQLSchema,
        fragments: JsonDict,
        root_value: Optional[type],
        operation: OperationDefinition,
        variable_values: JsonDict,
        context: HttpRequest,
        path: Optional[Union[List[Union[int, str]], List[str]]] = None,
    ) -> None:
        self.field_name = field_name
        self.field_asts = field_asts
        self.return_type = return_type
        self.parent_type = parent_type
        self.schema = schema
        self.fragments = fragments
        self.root_value = root_value
        self.operation = operation
        self.variable_values = variable_values
        self.context = context
        self.path = path
