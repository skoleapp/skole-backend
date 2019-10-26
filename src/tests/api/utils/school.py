from core.models import School
from core.utils import UNIVERSITY

SCHOOL_LIST_API_URL = reverse("school-list")


def school_detail_api_url(school_id):
    return reverse("school-detail", args=[school_id])


def school_list_filter_api_url(school_type):
    return f"/api/school/?school_type={school_type}/"


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
