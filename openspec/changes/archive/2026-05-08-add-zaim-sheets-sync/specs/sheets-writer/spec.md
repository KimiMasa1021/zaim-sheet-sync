## ADDED Requirements

### Requirement: Service Account 認証

The system SHALL authenticate to Google Sheets using `GOOGLE_SERVICE_ACCOUNT_JSON` (JSON文字列環境変数) by writing it to a temporary file and passing the path to `gspread.service_account()`. The temporary file SHALL be deleted after gspread initialization regardless of success or failure.

#### Scenario: 認証成功と一時ファイル削除

- **WHEN** `SheetsClient()` を初期化する
- **THEN** `GOOGLE_SERVICE_ACCOUNT_JSON` の内容を一時ファイルに書き込み、`gspread.service_account(filename=...)` を呼び、その後一時ファイルが `os.unlink` で削除される

#### Scenario: gspread 初期化失敗時もファイルは削除される

- **WHEN** `gspread.service_account()` が例外を投げる
- **THEN** `try/finally` により一時ファイルが必ず削除される

### Requirement: zaim_id 重複チェック

The system SHALL provide a method `get_existing_zaim_ids()` that returns a `set` of existing `zaim_id` values (as strings) from the `raw_data` sheet.

#### Scenario: 既存IDの取得

- **GIVEN** raw_data シートに zaim_id が `"1"` と `"2"` のレコードが存在する
- **WHEN** `get_existing_zaim_ids()` を呼び出す
- **THEN** `{"1", "2"}` を返す

#### Scenario: 空シート

- **GIVEN** raw_data シートにヘッダのみでレコードがない
- **WHEN** `get_existing_zaim_ids()` を呼び出す
- **THEN** 空集合 `set()` を返す

### Requirement: レコード追記

The system SHALL provide a method `append_records(records)` that appends rows to the `raw_data` sheet in the column order: `zaim_id`, `date`, `amount`, `name`, `genre`(空), `match_type`(空), `classified_at`(空).

#### Scenario: 新規レコードの追記

- **WHEN** `append_records([{"zaim_id": "3", "date": "2026-05-07", "amount": 300, "name": "test"}])` を呼び出す
- **THEN** raw_data の末尾に `["3", "2026-05-07", 300, "test", "", "", ""]` が1行追記される

#### Scenario: 空リストの場合は書き込まない

- **WHEN** `append_records([])` を呼び出す
- **THEN** `worksheet.append_rows` は呼ばれない

### Requirement: master シートの priority 昇順取得

The system SHALL provide a method `get_master()` that returns master sheet records sorted by `priority` ascending (smallest first).

#### Scenario: priority 昇順ソート

- **GIVEN** master シートに priority=2 のレコードと priority=1 のレコードが順不同で存在する
- **WHEN** `get_master()` を呼び出す
- **THEN** priority=1 のレコードが先頭、priority=2 のレコードが2番目になる

### Requirement: genre シート全件取得

The system SHALL provide a method `get_genres()` that returns all records from the `genre` sheet in the order they appear in the sheet.

#### Scenario: genre 取得

- **GIVEN** genre シートに3件のジャンル定義がある
- **WHEN** `get_genres()` を呼び出す
- **THEN** 3件のレコードがリストで返される
