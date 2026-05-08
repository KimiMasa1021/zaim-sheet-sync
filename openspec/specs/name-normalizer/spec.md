# name-normalizer Specification

## Purpose
TBD - created by archiving change add-zaim-sheets-sync. Update Purpose after archive.
## Requirements
### Requirement: 5ステップの正規化処理

The system SHALL normalize an input string by applying the following 5 steps in order:

1. 全角英数字・記号を半角に統一（`unicodedata.normalize("NFKC", ...)`）
2. 半角カナを全角カナに統一（同じく NFKC で吸収される）
3. 英字を小文字化（`str.lower()`）
4. 連続する空白文字を1つに圧縮（`re.sub(r"\s+", " ", ...)`）
5. 前後の空白を除去（`str.strip()`）

#### Scenario: 全角英数字の正規化

- **WHEN** `normalize("Ａｍａｚｏｎ")` を呼び出す
- **THEN** `"amazon"` を返す

#### Scenario: 半角カナの正規化

- **WHEN** `normalize("ｾﾌﾞﾝｲﾚﾌﾞﾝ")` を呼び出す
- **THEN** `"セブンイレブン"` を返す（濁点も結合される）

#### Scenario: 大文字の正規化

- **WHEN** `normalize("SEVEN")` を呼び出す
- **THEN** `"seven"` を返す

#### Scenario: 空白の圧縮と除去

- **WHEN** `normalize("  セブン  イレブン  ")` を呼び出す
- **THEN** `"セブン イレブン"` を返す（前後trim、連続空白は1つに）

#### Scenario: 全ステップの複合

- **WHEN** `normalize("  Ａｍａｚｏｎ　ｾﾌﾞﾝ  ")` を呼び出す
- **THEN** `"amazon セブン"` を返す

### Requirement: マスタキーワードへの同一処理適用

The system SHALL apply the same normalization function to master sheet keywords before substring matching against record names. This ensures consistent comparison regardless of input format.

#### Scenario: マスタも正規化対象

- **WHEN** master シートのキーワード `"Ａｍａｚｏｎ"` と raw_data の name `"amazonジャパン"` を比較する
- **THEN** 両方が `"amazon"` / `"amazonジャパン"` に正規化された上で部分一致が成立する

