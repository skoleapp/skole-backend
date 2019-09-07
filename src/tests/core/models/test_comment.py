def test_str(comment):
    comment.text = "Please help me with this"
    assert str(comment) == "testuser: Please help me with ..."

    comment.text = "Please help me"
    assert str(comment) == "testuser: Please help me"
