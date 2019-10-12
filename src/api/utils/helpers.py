"""General helper functions that can be used anywhere in api."""
from graphql.language.ast import FragmentSpread


def get_requested_fields(info):
    """Get list of fields requested in a query."""
    fragments = info.fragments

    def iterate_field_names(prefix, field):
        name = field.name.value
        if isinstance(field, FragmentSpread):
            results = []
            new_prefix = prefix
            sub_selection = fragments[name].selection_set.selections
        else:
            results = [prefix + name]
            new_prefix = prefix + name + '.'
            sub_selection = \
                field.selection_set.selections if field.selection_set else []
        for sub_field in sub_selection:
            results += iterate_field_names(new_prefix, sub_field)
        return results

    results = iterate_field_names('', info.field_asts[0])
    return results
