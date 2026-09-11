from course import LESSON


def test_checkpoint_is_identifiable():
    assert isinstance(LESSON, int)
    assert 0 <= LESSON <= 12

