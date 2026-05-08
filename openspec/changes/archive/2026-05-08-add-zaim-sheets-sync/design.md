## Context

家計簿アプリ「Zaim」と Google スプレッドシートを橋渡しする CI/CD パイプラインの初期実装。Zaim 単体ではジャンル管理に柔軟性がなく、独自のキーワード×ジャンルマスタで分類した上でスプレッドシートに集約したい。実行頻度は1日1回でよく、低コスト・低運用負荷で構築する必要がある。

外部依存は Zaim API（OAuth 1.0a）と Google Sheets API（Service Account）。実行基盤は GitHub Actions（無料枠）、分類処理は Claude Code Routines（Pro 1日5回制限）を利用する。

## Goals / Non-Goals

**Goals:**

- 毎日の支出データ取得→Sheets書き込み→分類起動を完全自動化する
- 重複登録を防ぐ仕組み（zaim_id ユニークキー）を持つ
- 一時的な外部APIエラーに対して耐性を持つ（5xxリトライ）
- 認証情報をコードから完全に分離する（GitHub Secrets / Routines 設定で管理）
- ジャンル分類を Zaim のカテゴリではなく独自マスタで柔軟に管理可能にする

**Non-Goals:**

- リアルタイム同期（バッチ1日1回で十分）
- 過去データの一括移行（前日分のみ取得）
- Zaim 側の収入データ・カテゴリ・口座情報の同期（支出のみ対象）
- スマホ・Web UI の提供（スプレッドシートを UI として使う）
- 月次レポート・予算アラート（将来拡張）

## Decisions

### 重複判定キーは `zaim_id` を採用

| 案 | 採否 | 理由 |
|---|---|---|
| `zaim_id` 単独 | ✅ 採用 | Zaim 側で発行される一意IDで衝突しない |
| `date + name + amount` | ❌ 却下 | 同日同店同額の支出が現実的に発生する（コンビニで2回など） |

### Zaim 取得は前日分のみに限定

GitHub Actions の cron は UTC基準で `0 0 * * *`（= 09:00 JST）。当日分は記録漏れの可能性が高いため、前日 `00:00-23:59` の確定データのみ取得する。

### 正規化に `unicodedata.NFKC` を採用

| 案 | 採否 | 理由 |
|---|---|---|
| NFKC + lower + 空白整形 | ✅ 採用 | 標準ライブラリのみで全角→半角・半角カナ→全角カナを一括処理可能 |
| 自作変換テーブル | ❌ 却下 | 保守コストが高く、エッジケースを取りこぼしやすい |

### 分類ロジックは Claude Code Routines に委譲

GitHub Actions 側で機械的なキーワードマッチを実装することも可能だが、

- マスタ未登録キーワードに対する曖昧マッチや表記ゆれ吸収を Routines（LLM）に任せられる
- 将来 master シートのレビューフロー導入時にプロンプトのみで挙動調整できる

の理由から、分類処理は Routines に分離する。GitHub Actions は Webhook を叩くだけ。

### Webhook 失敗時は処理続行

Sheets 書き込みは成功しているので、Webhook POST が失敗してもジョブ全体は失敗扱いにしない（warningログのみ）。Routines は Sheets 上の「genre 列が空」をトリガーに動くため、次回起動時に巻き戻し可能。

### 認証情報の受け渡し

`GOOGLE_SERVICE_ACCOUNT_JSON` は環境変数（JSON文字列）で受け取り、`tempfile.NamedTemporaryFile` 経由で `gspread.service_account()` に渡す。一時ファイルは `try/finally` で確実に削除する。

## Risks / Trade-offs

- **[Zaim API レート制限超過]** → 1日1回・前日分のみで余裕を持たせる。リトライは指数バックオフで4回まで（1初回 + 3リトライ）
- **[Google Sheets API クォータ枯渇]** → 1日のリクエスト数は数十件程度で無料枠を超えない見込み
- **[Routines 1日5回制限到達]** → 1日1回起動なので問題ないが、手動 workflow_dispatch を多用すると逼迫する可能性あり
- **[Routines Webhook の信頼性]** → POST 失敗を許容する設計にしているため一過性の障害には耐性あり。継続的に失敗する場合はログ監視が必要
- **[Service Account 鍵の漏洩リスク]** → GitHub Secrets で管理 + 一時ファイルを処理後に必ず削除。リポジトリは Private 前提
- **[Zaim 側の name 表記揺れ]** → 正規化で吸収しきれない場合は master に複数キーワードを登録する運用でカバー。`unmatched` として残すことで取りこぼしを検出可能

## Migration Plan

初期実装のため移行不要。デプロイ手順は以下：

1. GitHub Secrets に7種のシークレットを登録
2. Google Sheets を作成し、`raw_data` / `master` / `genre` シートをヘッダ付きで初期化
3. Service Account にスプレッドシートを共有
4. Claude Code Routines を作成し、`/v1/routines/<id>/trigger` の URL を `ROUTINE_WEBHOOK_URL` に設定
5. PR マージ後、`workflow_dispatch` で初回手動実行して動作確認

ロールバック：cron を停止（ワークフローの `on.schedule` を一時的にコメントアウト）し、Sheets 側のデータは手動で退避。

## Open Questions

- master シートの初期投入はどの粒度で行うか？（最低限のキーワード10件程度から始めて運用しながら追加する想定）
- `unmatched` レコードのレビュー頻度・運用フローは別チケットで設計（今チケットでは「unmatched としてマークされる」までを扱う）
