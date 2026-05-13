# zaim-sheet-sync

Zaim APIから支出明細を取得しGoogle スプレッドシートへ同期・分類するCI/CDパイプライン。

## セットアップ

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
# .env を編集して各値を設定
```

## 実行

```bash
python src/main.py
```

## テスト

```bash
pytest tests/ -v
```

## ⚠️ Zaim API の既知の制限事項

### 銀行・クレジットカードの自動連携データは取得不可

Zaim には金融機関と自動連携してデータを取り込む機能がありますが、**Zaim 公式 API 経由ではこの自動連携データにアクセスできません。**  
これはプランに関わらず（無料・プレミアム問わず）、API の仕様上の制限です。

> 「Zaim にはクレジットカードや銀行口座から自動でデータ取得する機能があるが、API ではそれらのデータにはアクセスできない」  
> — [pyzaim (GitHub)](https://github.com/liebe-magi/pyzaim)

そのため本システムで取得できるのは、**Zaim アプリ上で手動入力した支出レコードのみ**です。

自動連携データを扱いたい場合の代替手段：
- Zaim アプリで手動入力する
- 各金融機関の明細を CSV 等でエクスポートして Zaim に手動インポートする
- [pyzaim](https://github.com/liebe-magi/pyzaim) のような Selenium ベースのスクレイピングライブラリを利用する（非公式）

## ライセンス

MIT
