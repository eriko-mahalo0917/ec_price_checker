############################################################
#csvを扱うために
import csv
import os
import sys
#時刻や日付を取得するのに使う
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__),"../"))

#自作
from utils.logger import SimpleLogger
from utils.path_helper import get_root_path
from config import (
    CSV_REPORT_TITLE,
    CSV_SUMMARY_HEADERS,
    CSV_LIST_TITLE,
    CSV_PRODUCT_HEADERS
)
############################################################

class CsvSaver:
    def __init__(self):
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()

    # -----------------------
    # 1つ目のフロー
    # CSVファイル名を生成する
    # 同日・同キーワードで既にファイルがあれば _2, _3 と連番を付ける
    # -----------------------
    def build_filename(self, keyword: str, data_dir: str) -> str:
        # 今日の日付を yyyymmdd 形式で取得
        today = datetime.now().strftime("%Y%m%d")
        # スペースはアンダースコアに置換してファイル名を安全にする
        safe_keyword = keyword.replace(" ", "_").replace("　", "_")

        # 連番なしを試し、存在すれば _2, _3 … と増やす
        base = f"{today}_{safe_keyword}"
        filename = f"{base}.csv"
        count = 2
        while os.path.exists(os.path.join(data_dir, filename)):
            filename = f"{base}_{count}.csv"
            count += 1

        return filename

    # -----------------------
    # 2つ目のフロー
    # 保存先のパスを組み立てる
    # -----------------------
    def build_filepath(self, filename: str) -> str:
        data_dir = os.path.join(get_root_path(), "data")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, filename)

    # -----------------------
    # 3つ目のフロー
    # CSVに書き出す
    # keyword     : 検索キーワード（文字列）
    # summary     : 価格サマリー辞書 { min_price, avr_price, max_price }
    # product_list: 商品リスト list[dict]  ← price / name / shop / url を持つこと
    # count       : フィルター後の有効件数
    # -----------------------
    def save(self, keyword: str, summary: dict, product_list: list[dict], count: int) -> str:
        # data_dir を先に確定してから重複チェック付きのファイル名を生成する
        data_dir = os.path.join(get_root_path(), "data")
        os.makedirs(data_dir, exist_ok=True)

        filename  = self.build_filename(keyword, data_dir)
        filepath  = self.build_filepath(filename)

        self.logger.info(f"CSVの保存を開始します：{filepath}")

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)

            # ── サマリーセクション ──────────────────────────────
            writer.writerow([CSV_REPORT_TITLE])
            # ヘッダー行（configの日本語を使用）
            writer.writerow(list(CSV_SUMMARY_HEADERS.values()))
            # データ行
            writer.writerow([
                keyword,
                summary.get("min_price", ""),
                summary.get("avr_price", ""),
                summary.get("max_price", ""),
                count,
            ])

            # 区切り行
            writer.writerow([])

            # ── 商品一覧セクション ─────────────────────────────
            writer.writerow([CSV_LIST_TITLE])
            # ヘッダー行（configの日本語を使用）
            writer.writerow(CSV_PRODUCT_HEADERS)
            # 商品データを1行ずつ書き込む
            for product in product_list:
                writer.writerow([
                    product.get("price",        ""),
                    product.get("name",         ""),
                    product.get("shop",         ""),
                    product.get("url",          ""),
                    product.get("review_avg",   ""),
                    product.get("review_count", ""),
                ])

        self.logger.info(f"CSV保存完了：{filename}")
        return filepath
