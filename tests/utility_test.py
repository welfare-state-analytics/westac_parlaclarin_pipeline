from workflow.utility import dotget


def test_dotget():

    assert dotget({}, "apa", None) is None
    assert dotget({}, "apa", "olle") == "olle"
    assert dotget({}, "apa.olle", "olle") == "olle"
    assert dotget({'olle': 99}, "olle") == 99
    assert dotget({'olle': 99}, "olle.olle") is None
    assert dotget({'olle': {'kalle': 99, 'erik': 98}}, "olle.olle") is None
    assert dotget({'olle': {'kalle': 99, 'erik': 98}}, "olle.erik") == 98
    assert dotget({'olle': {'kalle': 99, 'erik': 98}}, "olle.kalle") == 99
    assert dotget({'olle': {'kalle': 99, 'erik': 98}}, ["olle.kalle"]) == 99
    assert dotget({'olle': {'kalle': 99, 'erik': 98}}, ["erik", "olle.kalle"]) == 99
