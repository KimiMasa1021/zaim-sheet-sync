## Why

Zaim に手動入力した支出データを Google スプレッドシートで自動的に可視化・分類したいが、現在は手動転記が必要で運用が破綻している。GitHub Actions と Claude Code Routines を組み合わせ、毎日の取得→正規化→重複排除→分類までを自動化する CI/CD パイプラインを構築する。

## What Changes

- Zaim API (OAuth 1.0a) から前日分の支出明細を取得する Python クライアントを追加
- 取得データの `name` を NFKC 正規化（全半角統一・小文字化・空白整形）する処理を追加
- gspread 経由で Google スプレッドシート（`raw_data` / `master` / `genre`）への読み書き機能を追加
- `zaim_id` を一意キーとした重複排除ロジックを追加
- 同期完了後に Webhook を叩いて Claude Code Routines を起動する仕組みを追加
- GitHub Actions ワークフロー（毎日 09:00 JST + 手動実行）を追加
- pytest による単体テスト一式を追加

## Capabilities

### New Capabilities

- `zaim-fetch`: Zaim API から前日分の支出明細を OAuth 1.0a で取得し、id・date・amount・name を返す（401即時失敗、5xxは指数バックオフで最大3回リトライ）
- `name-normalizer`: 支出名を5ステップ（全角→半角、半角カナ→全角カナ、小文字化、空白圧縮、trim）で正規化
- `sheets-writer`: Google スプレッドシート（raw_data・master・genre）の読み書きを担う。zaim_id 重複チェック、レコード追記、master の priority 昇順取得
- `classify-routine`: Claude Code Routines が webhook 起動で raw_data の未分類レコードに master を部分一致させて genre/match_type/classified_at を書き込む

### Modified Capabilities

（なし — 初期実装のため既存 capability の変更はない）

## Impact

- **新規追加**: `src/{zaim_client,normalizer,sheets_client,main}.py`、`tests/test_*.py`、`conftest.py`
- **依存追加**: `requests-oauthlib`（OAuth 1.0a）、`gspread`（Sheets操作）、開発用に `pytest-mock`
- **GitHub Secrets**: `ZAIM_*` 4種、`GOOGLE_SERVICE_ACCOUNT_JSON`、`SPREADSHEET_ID`、`ROUTINE_WEBHOOK_URL` の設定が必要
- **外部システム**: Zaim API（v2.1.0）、Google Sheets API、Claude Code Routines（Pro以上、1日5回制限）
- **運用**: 毎日 09:00 JST に自動実行、コストは GitHub Actions 無料枠内で完結
