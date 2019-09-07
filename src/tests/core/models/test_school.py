def test_str(school):
    assert str(school) == "University of Test"

    school.name = "Aalto University"
    assert str(school) == "Aalto University"
