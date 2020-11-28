"""
The constants in this module are used in object type, query, and mutation descriptions
that are injected to API docs.

Descriptions must be single-line to have a decent formatting on the GraphiQL.
Descriptions are also not translated as they are only used for improved developer
experience and proper API documentation.
"""

AUTH_REQUIRED = "Only allowed for authenticated users."
VERIFICATION_REQUIRED = (
    "Only allowed for authenticated users that have verified their accounts."
)
OWNERSHIP_REQUIRED = "Only allowed for users that are the creators of the object."
DETAIL_QUERY = (
    "Return a single object based on the ID. If an object is not found "
    "or it has been soft deleted, return `null` instead."
)
AUTOCOMPLETE_QUERY = "Return limited amount of results for autocomplete fields."
PAGINATED = "Results are paginated."
