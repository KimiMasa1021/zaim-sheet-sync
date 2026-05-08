from normalizer import normalize


def test_fullwidth_alphanumeric():
    assert normalize("Ａｍａｚｏｎ") == "amazon"


def test_halfwidth_kana():
    assert normalize("ｾﾌﾞﾝｲﾚﾌﾞﾝ") == "セブンイレブン"


def test_uppercase():
    assert normalize("SEVEN") == "seven"


def test_compress_and_strip_whitespace():
    assert normalize("  セブン  イレブン  ") == "セブン イレブン"


def test_combined_all_steps():
    assert normalize("  Ａｍａｚｏｎ　ｾﾌﾞﾝ  ") == "amazon セブン"
