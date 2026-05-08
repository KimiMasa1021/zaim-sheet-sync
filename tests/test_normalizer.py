from normalizer import normalize


def test_fullwidth_alphanumeric():
    assert normalize("Ａｍａｚｏｎ") == "amazon"


def test_halfwidth_kana():
    assert normalize("ｾﾌﾞﾝｲﾚﾌﾞﾝ") == "セブンイレブン"


def test_lowercase():
    assert normalize("SEVEN") == "seven"


def test_compress_whitespace():
    assert normalize("セブン  イレブン") == "セブン イレブン"


def test_strip():
    assert normalize("  Amazon  ") == "amazon"


def test_combined():
    assert normalize("  Ａｍａｚｏｎ　ｾﾌﾞﾝ  ") == "amazon セブン"
