import pytest
from unittest.mock import MagicMock, patch

from zaim_client import ZaimAuthError, ZaimClient


@pytest.fixture(autouse=True)
def zaim_env(monkeypatch):
    monkeypatch.setenv("ZAIM_CONSUMER_KEY", "ck")
    monkeypatch.setenv("ZAIM_CONSUMER_SECRET", "cs")
    monkeypatch.setenv("ZAIM_ACCESS_TOKEN", "at")
    monkeypatch.setenv("ZAIM_ACCESS_TOKEN_SECRET", "ats")


@patch("zaim_client.OAuth1Session")
def test_fetch_returns_records(mock_session_cls):
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {
        "money": [{"id": 1, "date": "2026-05-07", "amount": 500, "name": "test"}]
    }
    mock_session_cls.return_value.get.return_value = mock_resp

    records = ZaimClient().fetch_yesterday()

    assert records == [{"zaim_id": "1", "date": "2026-05-07", "amount": 500, "name": "test"}]


@patch("zaim_client.OAuth1Session")
def test_fetch_raises_on_401(mock_session_cls):
    mock_resp = MagicMock(status_code=401)
    mock_session_cls.return_value.get.return_value = mock_resp

    with pytest.raises(ZaimAuthError):
        ZaimClient().fetch_yesterday()


@patch("zaim_client.time.sleep")
@patch("zaim_client.OAuth1Session")
def test_fetch_retries_on_5xx(mock_session_cls, mock_sleep):
    mock_500 = MagicMock(status_code=500)
    mock_200 = MagicMock(status_code=200)
    mock_200.json.return_value = {"money": []}
    mock_session_cls.return_value.get.side_effect = [mock_500, mock_200]

    records = ZaimClient().fetch_yesterday()

    assert records == []
    assert mock_session_cls.return_value.get.call_count == 2
    mock_sleep.assert_called_once_with(1)


@patch("zaim_client.OAuth1Session")
def test_fetch_uses_place_for_payment(mock_session_cls):
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {
        "money": [
            {"id": 10, "date": "2026-05-09", "amount": 980, "place": "ローソン", "name": ""},
            {"id": 11, "date": "2026-05-09", "amount": 100000, "place": "", "name": "給与"},
        ]
    }
    mock_session_cls.return_value.get.return_value = mock_resp

    records = ZaimClient().fetch_yesterday()

    assert records[0]["name"] == "ローソン"
    assert records[1]["name"] == "給与"


@patch("zaim_client.OAuth1Session")
def test_fetch_range_passes_dates(mock_session_cls):
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {
        "money": [{"id": 7, "date": "2026-05-03", "amount": 100, "name": "x"}]
    }
    mock_get = mock_session_cls.return_value.get
    mock_get.return_value = mock_resp

    records = ZaimClient().fetch_range("2026-05-01", "2026-05-10")

    assert records == [{"zaim_id": "7", "date": "2026-05-03", "amount": 100, "name": "x"}]
    _, kwargs = mock_get.call_args
    assert kwargs["params"]["start_date"] == "2026-05-01"
    assert kwargs["params"]["end_date"] == "2026-05-10"


@patch("zaim_client.OAuth1Session")
def test_fetch_empty_money(mock_session_cls):
    mock_resp = MagicMock(status_code=200)
    mock_resp.json.return_value = {"money": []}
    mock_session_cls.return_value.get.return_value = mock_resp

    assert ZaimClient().fetch_yesterday() == []
