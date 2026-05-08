# name-normalizer Specification

## Purpose
支出名（name）を正規化してキーワードマッチ精度を向上させる。

## Requirements

### Requirement: 正規化処理
The system SHALL apply the following normalization steps in order:
1. 全角英数字・記号を半角に統一（unicodedata NFKC）
2. 半角カナを全角カナに統一（unicodedata NFKC）
3. 英字を小文字化
4. 連続する空白を1つに圧縮
5. 前後の空白を除去

#### Scenario: 全角英数字の正規化
- GIVEN name が "Ａｍａｚｏｎ" である
- WHEN `normalize()` を呼び出す
- THEN "amazon" を返す

#### Scenario: 半角カナの正規化
- GIVEN name が "ｾﾌﾞﾝｲﾚﾌﾞﾝ" である
- WHEN `normalize()` を呼び出す
- THEN "セブンイレブン" を返す

#### Scenario: 複合正規化
- GIVEN name が "  Ａｍａｚｏｎ　" である
- WHEN `normalize()` を呼び出す
- THEN "amazon" を返す

### Requirement: マスタキーワードへの適用
The system SHALL apply the same normalization to master sheet keywords before comparison.
