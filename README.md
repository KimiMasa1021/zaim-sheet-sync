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

## ライセンス

MIT
