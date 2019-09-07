def test_str(db, school):
    school1 = school()
    assert str(school1) == "University of Test"

    school2 = school(name="Aalto University")
    assert str(school2) == "Aalto University"
