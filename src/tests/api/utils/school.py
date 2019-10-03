from core.models import School
from core.utils import UNIVERSITY


def sample_school(**params):
    if "school_type" in params:
        school_type = params["school_type"].lower().replace("_", " ")
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
