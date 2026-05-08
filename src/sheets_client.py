import os
import tempfile

import gspread


class SheetsClient:
    def __init__(self):
        creds_json = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        try:
            tmp.write(creds_json)
            tmp.close()
            gc = gspread.service_account(filename=tmp.name)
        finally:
            os.unlink(tmp.name)
        self._sh = gc.open_by_key(os.environ["SPREADSHEET_ID"])

    def get_existing_zaim_ids(self) -> set:
        ws = self._sh.worksheet("raw_data")
        return {str(r["zaim_id"]) for r in ws.get_all_records() if r.get("zaim_id")}

    def append_records(self, records: list[dict]) -> None:
        ws = self._sh.worksheet("raw_data")
        rows = [
            [r["zaim_id"], r["date"], r["amount"], r["name"], "", "", ""]
            for r in records
        ]
        if rows:
            ws.append_rows(rows, value_input_option="RAW")

    def get_master(self) -> list[dict]:
        ws = self._sh.worksheet("master")
        return sorted(ws.get_all_records(), key=lambda r: int(r.get("priority", 9999)))

    def get_genres(self) -> list[dict]:
        ws = self._sh.worksheet("genre")
        return ws.get_all_records()
