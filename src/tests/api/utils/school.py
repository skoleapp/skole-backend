from graphene_django.utils import GraphQLTestCase
from mypy.types import JsonDict

from app.models import School
from app.utils import UNIVERSITY


def create_sample_school(**params: str) -> School:
    if "school_type" in params:
        school_type = params["school_type"]
    else:
        school_type = UNIVERSITY

    defaults = {
        "school_type": school_type,
        "name": f"Test {school_type}",
        "city": "Turku",
        "country": "Finland",
    }

    defaults.update(params)
    school = School.objects.create(**defaults)
    return school


def query_schools(test_cls: GraphQLTestCase) -> JsonDict:
    query = \
        """
        query {
          schools {
            id
            name
            schoolType
            city
            country
          }
        }
        """

    return test_cls.client.execute(
        query,
    )


def query_school(test_cls: GraphQLTestCase, id_: int = 1) -> JsonDict:
    variables = {"id": id_}

    query = \
        """
        query school($id: Int!) {
         school(id: $id) {
           id
           name
           schoolType
           city
           country
         }
        }
        """

    return test_cls.client.execute(
        query,
        variables=variables,
    )
