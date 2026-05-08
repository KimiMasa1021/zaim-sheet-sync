## ADDED Requirements

### Requirement: OAuth 1.0a 認証

The system SHALL authenticate Zaim API requests using OAuth 1.0a with the four credentials supplied via environment variables: `ZAIM_CONSUMER_KEY`, `ZAIM_CONSUMER_SECRET`, `ZAIM_ACCESS_TOKEN`, `ZAIM_ACCESS_TOKEN_SECRET`.

#### Scenario: 認証情報が揃っている

- **WHEN** すべての環境変数が設定された状態で `ZaimClient` を初期化する
- **THEN** `OAuth1Session` が4つの認証情報を使って構築される

#### Scenario: 認証情報が欠けている

- **WHEN** いずれかの環境変数が未設定の状態で `ZaimClient` を初期化する
- **THEN** `KeyError` が発生する（fail-fast）

### Requirement: 前日分の支出明細取得

The system SHALL fetch yesterday's expense records via `GET https://api.zaim.net/v2/home/money` with `mapping=1`, `start_date` and `end_date` set to yesterday in `Y-m-d` format.

#### Scenario: 前日分の取得

- **WHEN** `fetch_yesterday()` を呼び出す
- **THEN** `start_date = end_date = (今日 - 1日)` で `GET /v2/home/money` を呼ぶ

#### Scenario: 必要フィールドのみ抽出

- **WHEN** Zaim API が money 配列を返す
- **THEN** 各要素から `id`（→`zaim_id`、文字列化）・`date`・`amount`・`name` のみを抽出して返す

#### Scenario: 取得件数ゼロ

- **WHEN** Zaim API が `{"money": []}` を返す
- **THEN** 空リストを返し正常終了する

### Requirement: 401 エラー時の即時失敗

The system SHALL raise `ZaimAuthError` immediately when Zaim API returns HTTP 401 and SHALL NOT retry.

#### Scenario: 認証失敗

- **WHEN** Zaim API が 401 を返す
- **THEN** `ZaimAuthError` が発生し、リトライせず即時終了する

### Requirement: 5xx エラー時の指数バックオフリトライ

The system SHALL retry up to 3 times with exponential backoff (1s → 2s → 4s) when Zaim API returns 5xx errors. After 3 retries (4 total attempts), the system SHALL raise the final HTTP error.

#### Scenario: 一過性の 500 エラーから回復

- **WHEN** Zaim API が1回目500、2回目200を返す
- **THEN** 1秒待機後リトライし、2回目のレスポンスを正常に返す

#### Scenario: リトライ上限到達

- **WHEN** Zaim API が4回連続で500を返す
- **THEN** 1s + 2s + 4s 待機後、4回目で `requests.HTTPError` が発生する
