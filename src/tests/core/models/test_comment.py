def test_str(db, comment):
    comment1 = comment(text="Please help me with this")
    assert str(comment1) == "testuser: Please help me with ..."

    comment1.text = "Please help me"
    assert str(comment1) == "testuser: Please help me"
