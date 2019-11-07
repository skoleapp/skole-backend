from pytest import fixture


def test_str(school: fixture) -> None:
    assert str(school) == "University of Test"

    school.name = "Aalto University"
    assert str(school) == "Aalto University"
