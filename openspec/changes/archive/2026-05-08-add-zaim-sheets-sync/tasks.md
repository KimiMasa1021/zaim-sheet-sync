## 1. プロジェクト構造のセットアップ

- [x] 1.1 `src/` と `tests/` ディレクトリを作成
- [x] 1.2 ルートに `conftest.py` を配置し `src/` を `sys.path` に追加（pytest がモジュールを解決できるようにする）

## 2. name-normalizer 実装

- [x] 2.1 `src/normalizer.py` に `normalize(text: str) -> str` を実装（NFKC → lower → 連続空白圧縮 → strip）
- [x] 2.2 `tests/test_normalizer.py` で5シナリオ（全角英数字・半角カナ・大文字・空白圧縮・複合）をカバー

## 3. zaim-fetch 実装

- [x] 3.1 `src/zaim_client.py` に `ZaimAuthError` 例外クラスを定義
- [x] 3.2 `src/zaim_client.py` に `ZaimClient` クラスを実装（OAuth1Session で4認証情報を受け取る）
- [x] 3.3 `fetch_yesterday()` メソッドを実装（前日分の日付計算 → `_fetch_money` 委譲）
- [x] 3.4 `_fetch_money(start_date, end_date)` を実装（`GET /v2/home/money` + `mapping=1`、id・date・amount・name のみ抽出）
- [x] 3.5 401 で `ZaimAuthError` を即時発生させる分岐を追加
- [x] 3.6 5xx で 1s → 2s → 4s の指数バックオフリトライを実装（最大3リトライ = 計4試行）
- [x] 3.7 `tests/test_zaim_client.py` で正常取得・401・5xxリトライ・空応答の4シナリオをカバー

## 4. sheets-writer 実装

- [x] 4.1 `src/sheets_client.py` の `SheetsClient.__init__` で `GOOGLE_SERVICE_ACCOUNT_JSON` を一時ファイルに書き出し → `gspread.service_account()` → `try/finally` で `os.unlink`
- [x] 4.2 `get_existing_zaim_ids() -> set` を実装（raw_data シートの zaim_id 列を文字列化して set で返す）
- [x] 4.3 `append_records(records: list[dict])` を実装（zaim_id・date・amount・name + 空3列を append_rows、空リストは no-op）
- [x] 4.4 `get_master() -> list[dict]` を実装（master シート全件 → `priority` 昇順ソート）
- [x] 4.5 `get_genres() -> list[dict]` を実装（genre シート全件取得）
- [x] 4.6 `tests/test_sheets_client.py` で5シナリオ（既存ID取得・追記・空追記・priorityソート・ジャンル取得）をカバー（gspread をモック）

## 5. classify-routine プロンプト整備

- [x] 5.1 `src/main.py` から `ROUTINE_WEBHOOK_URL` に `requests.post` で起動シグナルを送る処理を実装（失敗時は warning ログのみ）
- [x] 5.2 Routines 側のプロンプト本文を `openspec/changes/add-zaim-sheets-sync/specs/classify-routine/spec.md` に記載済みの仕様に従って Routines コンソールに登録（手動運用、コミット対象外）

## 6. main.py エントリーポイント

- [x] 6.1 `src/main.py` を作成し、`logging.basicConfig` で INFO 以上を標準出力に出す
- [x] 6.2 ZaimClient → fetch_yesterday → 例外時はエラーログ + raise（GitHub Actions を失敗扱い）
- [x] 6.3 各レコードの `name` を `normalize()` で正規化
- [x] 6.4 SheetsClient → `get_existing_zaim_ids()` で重複除外
- [x] 6.5 新規レコードのみ `append_records` で書き込み、件数とスキップ件数をログ出力
- [x] 6.6 `ROUTINE_WEBHOOK_URL` が設定されていれば POST、失敗時は warning ログ
- [x] 6.7 `if __name__ == "__main__": main()` ガードを追加

## 7. 依存関係と CI

- [x] 7.1 `requirements.txt` に `requests`, `requests-oauthlib`, `gspread` の3つが揃っていることを確認（既存）
- [x] 7.2 `requirements-dev.txt` に `pytest`, `pytest-mock` が揃っていることを確認（既存）
- [x] 7.3 `.github/workflows/sync.yml` の env で7種のシークレットが渡されていることを確認（既存）

## 8. 検証

- [x] 8.1 ローカルで `pytest tests/ -v` を実行し全テストが green になることを確認
- [x] 8.2 `openspec validate --change add-zaim-sheets-sync --strict` でスペック妥当性をチェック
- [x] 8.3 PR を更新してレビュー依頼
