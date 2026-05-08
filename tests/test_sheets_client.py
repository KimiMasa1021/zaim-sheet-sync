import json
import pytest
from unittest.mock import MagicMock, patch

from sheets_client import SheetsClient


@pytest.fixture(autouse=True)
def sheets_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", json.dumps({"type": "service_account"}))
    monkeypatch.setenv("SPREADSHEET_ID", "test-id")


@pytest.fixture
def mock_sh():
    return MagicMock()


@pytest.fixture
def client(mock_sh):
    mock_gc = MagicMock()
    mock_gc.open_by_key.return_value = mock_sh
    with patch("sheets_client.gspread.service_account", return_value=mock_gc):
        return SheetsClient()


def test_get_existing_zaim_ids(client, mock_sh):
    mock_ws = MagicMock()
    mock_sh.worksheet.return_value = mock_ws
    mock_ws.get_all_records.return_value = [
        {"zaim_id": "1", "date": "2026-05-07", "amount": 500, "name": "a"},
        {"zaim_id": "2", "date": "2026-05-07", "amount": 200, "name": "b"},
    ]

    assert client.get_existing_zaim_ids() == {"1", "2"}


def test_append_records(client, mock_sh):
    mock_ws = MagicMock()
    mock_sh.worksheet.return_value = mock_ws

    client.append_records([{"zaim_id": "3", "date": "2026-05-07", "amount": 300, "name": "c"}])

    args = mock_ws.append_rows.call_args[0][0]
    assert args[0][:4] == ["3", "2026-05-07", 300, "c"]


def test_append_records_empty(client, mock_sh):
    mock_ws = MagicMock()
    mock_sh.worksheet.return_value = mock_ws

    client.append_records([])

    mock_ws.append_rows.assert_not_called()


def test_get_master_sorted_by_priority(client, mock_sh):
    mock_ws = MagicMock()
    mock_sh.worksheet.return_value = mock_ws
    mock_ws.get_all_records.return_value = [
        {"keyword": "Amazon", "genre": "ネット通販", "priority": 2, "note": ""},
        {"keyword": "セブンイレブン", "genre": "コンビニ", "priority": 1, "note": ""},
    ]

    master = client.get_master()
    assert master[0]["keyword"] == "セブンイレブン"
    assert master[1]["keyword"] == "Amazon"


def test_get_genres(client, mock_sh):
    mock_ws = MagicMock()
    mock_sh.worksheet.return_value = mock_ws
    mock_ws.get_all_records.return_value = [
        {"genre_name": "コンビニ", "display_order": 2, "note": ""},
    ]

    genres = client.get_genres()
    assert genres[0]["genre_name"] == "コンビニ"
