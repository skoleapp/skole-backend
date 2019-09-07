def test_str(db, course):
    course1 = course()
    assert str(course1) == "TEST0001 Test course"

    course1.
