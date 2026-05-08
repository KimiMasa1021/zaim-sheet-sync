# zaim-fetch Specification

## Purpose
Zaim API (OAuth 1.0a) を用いて前日分の支出明細を取得し、zaim_id・date・amount・name を返す。

## Requirements

### Requirement: OAuth認証
The system SHALL authenticate using OAuth 1.0a with ZAIM_CONSUMER_KEY, ZAIM_CONSUMER_SECRET, ZAIM_ACCESS_TOKEN, ZAIM_ACCESS_TOKEN_SECRET.

### Requirement: 明細取得
The system SHALL fetch money records via `GET https://api.zaim.net/v2/home/money` with `mapping=1`, `start_date` and `end_date` set to yesterday (Y-m-d).

#### Scenario: 正常取得
- GIVEN 有効なOAuth認証情報が設定されている
- WHEN `fetch_yesterday()` を呼び出す
- THEN money配列から zaim_id・date・amount・name を抽出して返す

### Requirement: 認証エラー
The system SHALL raise ZaimAuthError immediately on 401 without retrying.

#### Scenario: 認証エラー
- GIVEN Zaim APIが401を返す
- WHEN `fetch_yesterday()` を呼び出す
- THEN ZaimAuthError を発生させ即時終了する

### Requirement: リトライ
The system SHALL retry up to 3 times with exponential backoff (1s → 2s → 4s) on 5xx errors.

#### Scenario: 一時エラーリトライ
- GIVEN Zaim APIが1回目500を返し2回目200を返す
- WHEN `fetch_yesterday()` を呼び出す
- THEN 1秒待機後リトライし正常なレスポンスを返す
