def test_str(course):
    assert str(course) == "TEST0001 Test course"

    course.code = None
    assert str(course) == "Test course"

    course.code = "TEST0001"
    course.name = None
    assert str(course) == "TEST0001"
