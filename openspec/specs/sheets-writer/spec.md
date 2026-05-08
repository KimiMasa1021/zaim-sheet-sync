# sheets-writer Specification

## Purpose
Google スプレッドシートへの読み書きを担う。raw_data・master・genre シートを操作する。

## Requirements

### Requirement: 認証
The system SHALL authenticate using GOOGLE_SERVICE_ACCOUNT_JSON (一時ファイル経由で `gspread.service_account()` に渡す).

### Requirement: zaim_id重複チェック
The system SHALL return a Set of existing zaim_id values from the raw_data sheet.

#### Scenario: 重複IDの取得
- GIVEN raw_data シートに2件のレコードがある
- WHEN `get_existing_zaim_ids()` を呼び出す
- THEN zaim_id の集合（Set）を返す

### Requirement: レコード追記
The system SHALL append new records (zaim_id, date, amount, name, genre="", match_type="", classified_at="") to the raw_data sheet.

#### Scenario: レコード追記
- GIVEN 新規レコード1件がある
- WHEN `append_records(records)` を呼び出す
- THEN raw_data シートの末尾に1行追記される

#### Scenario: 空リストの追記
- GIVEN records が空リストである
- WHEN `append_records([])` を呼び出す
- THEN シートへの書き込みは行われない

### Requirement: マスタ取得
The system SHALL return master sheet records sorted by priority ascending.

#### Scenario: priority昇順ソート
- GIVEN master シートに priority=2 と priority=1 のレコードがある
- WHEN `get_master()` を呼び出す
- THEN priority=1 のレコードが先頭になる

### Requirement: ジャンル取得
The system SHALL return all records from the genre sheet.
