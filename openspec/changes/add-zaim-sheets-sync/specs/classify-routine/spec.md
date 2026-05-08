## ADDED Requirements

### Requirement: Webhook 起動

The system SHALL be triggered by an HTTP POST webhook from GitHub Actions after raw_data sync completion. GitHub Actions side SHALL post to `ROUTINE_WEBHOOK_URL` and SHALL log a warning (not fail the job) if the POST fails.

#### Scenario: Sheets 書き込み完了後の Webhook POST

- **WHEN** raw_data への追記処理が完了する
- **THEN** `ROUTINE_WEBHOOK_URL` に `POST` リクエストが送信される

#### Scenario: Webhook POST 失敗時の継続

- **WHEN** Webhook POST が例外を発生させる
- **THEN** GitHub Actions ジョブは warning ログを記録した上で正常終了する（Sheets書き込みは完了済みのため）

### Requirement: 未分類レコードの抽出

The system SHALL identify records in `raw_data` whose `genre` column is empty as the targets for classification.

#### Scenario: 未分類のみ対象

- **GIVEN** raw_data に genre が `"コンビニ"` のレコードと genre が空のレコードが混在する
- **WHEN** classify-routine が起動される
- **THEN** genre が空のレコードのみが分類対象になる

### Requirement: priority 昇順でのキーワード部分一致

The system SHALL match each unclassified record's `name` against master keywords in priority-ascending order, using normalized substring matching. The first matching keyword SHALL determine the genre.

#### Scenario: priority の小さいキーワードが優先

- **GIVEN** master に `keyword="セブン", genre="コンビニ", priority=1` と `keyword="セブンイレブン専門店", genre="その他", priority=2` がある
- **WHEN** name `"セブンイレブン渋谷店"` を分類する
- **THEN** priority=1 が先にマッチするため genre は `"コンビニ"` になる

#### Scenario: 正規化後の部分一致

- **GIVEN** master のキーワード `"Ａｍａｚｏｎ"` と raw_data の name `"amazonジャパン"`
- **WHEN** 両者が name-normalizer で正規化される
- **THEN** `"amazon"` が `"amazonジャパン"` に部分一致し分類が成立する

### Requirement: 一致した場合の書き込み

When a master keyword matches, the system SHALL write to the `raw_data` row: `genre` = matched master's genre, `match_type` = `"keyword"`, `classified_at` = current ISO8601 timestamp with JST offset.

#### Scenario: 一致時の3列更新

- **WHEN** name `"セブンイレブン"` がキーワード `"セブンイレブン"` (genre=`"コンビニ"`) に一致する
- **THEN** 当該行の genre=`"コンビニ"`、match_type=`"keyword"`、classified_at=`"2026-05-08T09:15:00+09:00"` 形式の現在時刻が書き込まれる

### Requirement: 未一致の場合のフォールバック

When no master keyword matches, the system SHALL write `genre` = `"その他"`, `match_type` = `"unmatched"`, and `classified_at` = current timestamp.

#### Scenario: 未一致時のデフォルト分類

- **GIVEN** master にどのキーワードも name `"未知の店舗XYZ"` に一致しない
- **WHEN** classify-routine が当該レコードを処理する
- **THEN** genre=`"その他"`、match_type=`"unmatched"`、classified_at が書き込まれる

### Requirement: classified_at 形式

The system SHALL format `classified_at` as ISO 8601 with JST offset (`+09:00`).

#### Scenario: タイムスタンプ形式

- **WHEN** 分類結果を書き込む
- **THEN** `classified_at` は `YYYY-MM-DDTHH:MM:SS+09:00` 形式の文字列になる
