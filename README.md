# 楽天市場 価格チェッカー

楽天市場APIを使って商品の最安値・平均価格・最高価格を自動収集し、CSVに保存するツールです。

---

## 前提条件

| 項目 | バージョン |
|------|-----------|
| Python | 3.9 以上 |
| 楽天市場 API | アプリID・アクセスキー（要取得） |

> 楽天デベロッパーアカウントは [こちら](https://webservice.rakuten.co.jp/) から作成できます。

---

## セットアップ

### 1. リポジトリをクローン

```bash
git clone <リポジトリURL>
cd ec_price_checker
```

### 2. 仮想環境を作成・有効化

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

### 4. `.env` ファイルを作成

プロジェクト直下に `.env` を作成し、APIキーを設定します。

```
RAKUTEN_API_ID=your_application_id_here
RAKUTEN_ACCESS_KEY=your_access_key_here
```

---

## 使い方

### Python から実行

```bash
source venv/bin/activate
python main.py
```

### 実行ファイル（配布版）から実行

```
dist/
├── RakutenPriceChecker   ← これをダブルクリック or ターミナルから実行
└── .env                  ← APIキーをここに記入
```

---

## 操作手順

1. アプリを起動するとキーワード入力ダイアログが表示されます

   ```
   ┌─────────────────────────────────┐
   │  検索キーワードを入力してください  │
   │  ┌─────────────────────────┐   │
   │  │ プロテイン               │   │
   │  └─────────────────────────┘   │
   │         [キャンセル]  [OK]       │
   └─────────────────────────────────┘
   ```

2. キーワードを入力して **OK** を押すと検索が始まります

   - 単一キーワード：`プロテイン`
   - AND検索（複数キーワード）：`プロテイン,ソイ`

3. 処理完了後、ポップアップで保存先が表示されます

   ```
   ┌──────────────────────────────────────────────┐
   │  完了                                         │
   │  CSVの保存が完了しました。                     │
   │  /path/to/data/20260401_プロテイン.csv        │
   │                          [OK]                 │
   └──────────────────────────────────────────────┘
   ```

4. `data/` フォルダにCSVが保存されます

---

## 出力CSVのフォーマット

```
■ 検索統計レポート
検索キーワード,最安価格,平均価格,最高価格,有効ヒット件数
プロテイン,1980,3450,8800,142

■ 商品詳細（価格の安い順）
価格,商品名,ショップ名,商品URL,平均レビュー,レビュー件数
1980,〇〇プロテイン 1kg,サプリショップ,https://...,4.5,128
...
```

同日・同キーワードで複数回実行した場合はファイル名に連番が付きます。

```
data/
├── 20260401_プロテイン.csv
├── 20260401_プロテイン_2.csv
└── 20260401_プロテイン_3.csv
```

---

## プロジェクト構成

```
ec_price_checker/
├── main.py                   # エントリーポイント
├── main_flow.py              # 全体フロー制御
├── config.py                 # 定数・設定
├── .env                      # APIキー（要作成・Gitに含めない）
├── requirements.txt
├── api/
│   └── rakuten_api.py        # 楽天APIリクエスト・レスポンス整形
├── price_tools/
│   ├── price_list_builder.py # フィルタリング・並び替え
│   └── price_stats.py        # 価格統計（最安・平均・最高）
├── utils/
│   ├── csv_saver.py          # CSV生成・保存
│   ├── popup.py              # ダイアログ・ポップアップ（tkinter）
│   ├── logger.py             # ロギング設定
│   └── path_helper.py        # 実行環境パス解決（Python / exe 両対応）
└── dist/
    ├── RakutenPriceChecker   # 配布用実行ファイル
    └── .env                  # 配布用APIキー設定ファイル
```

---

## exe ファイルのビルド方法

```bash
source venv/bin/activate
pyinstaller --onefile --name "RakutenPriceChecker" main.py
```

ビルド後、`dist/.env` にAPIキーを設定してから配布してください。
