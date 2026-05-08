# classify-routine Specification

## Purpose
Claude Code Routines が genre・master シートを参照し、raw_data の未分類レコードにジャンルを付与する。

## Requirements

### Requirement: トリガー
The system SHALL be triggered by HTTP POST webhook from GitHub Actions after sync completion.

### Requirement: 分類処理
The system SHALL classify each unclassified record in raw_data (genre列が空) using the following logic:
- master シートのキーワードを priority 昇順で照合（部分一致）
- 一致した場合: genre = 対応するジャンル名、match_type = "keyword"
- 一致しない場合: genre = "その他"、match_type = "unmatched"
- classified_at = 処理日時（ISO8601+JST）を書き込む

#### Scenario: キーワード一致
- GIVEN raw_data に genre が空のレコード（name: "セブンイレブン渋谷店"）がある
- WHEN classify-routine が起動される
- THEN genre = "コンビニ"、match_type = "keyword"、classified_at が書き込まれる

#### Scenario: キーワード未一致
- GIVEN raw_data に genre が空のレコード（name: "未知の店舗"）がある
- WHEN classify-routine が起動される
- THEN genre = "その他"、match_type = "unmatched"、classified_at が書き込まれる

### Requirement: 正規化適用
The system SHALL apply the same normalization (name-normalizer spec) to both raw_data name values and master keywords before comparison.

### Requirement: Routinesプロンプト
The system SHALL use the following prompt template:

```
スプレッドシート（ID: {SPREADSHEET_ID}）の genre シートからジャンル定義を、
master シートからキーワードマスタを読み込み、raw_data シートの genre 列が
空のレコードを対象に支出をジャンル分類してください。
キーワードは部分一致で照合し、priority が小さい順に優先します。
一致しない場合は genre を「その他」、match_type を「unmatched」としてください。
分類結果（genre・match_type・classified_at）は raw_data シートの当該行に直接書き込んでください。
```
