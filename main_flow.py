############################################################
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "./")))

# 自作
from utils.logger import SimpleLogger
from api.rakuten_api import RakutenAPI
from price_tools.price_list_builder import PriceListBuilder
from price_tools.price_stats import PriceStats
from utils.csv_saver import CsvSaver
from utils.popup import PopupManager
############################################################

class MainFlow:
    def __init__(self):
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()

        self.api          = RakutenAPI()
        self.builder      = PriceListBuilder()
        self.stats        = PriceStats()
        self.csv_saver    = CsvSaver()

    # -----------------------
    # 1つ目のフロー
    # キーワードを入力してもらう
    # カンマ区切りで複数キーワードのAND検索に対応
    # 例）「青汁」「青汁,雑穀」「青汁, 雑穀米」
    # -----------------------
    def input_keywords(self) -> tuple[str, str]:
        # ダイアログでキーワードを入力（キャンセル時は ValueError）
        raw_input = PopupManager.ask_keywords()

            # カンマで分割して前後の空白を取り除く
        keyword_list = [kw.strip() for kw in raw_input.split(",") if kw.strip()]

        # 表示用キーワード（カンマ+スペース区切り）
        display_keyword = ", ".join(keyword_list)
        # 楽天API用キーワード（スペース区切り → AND検索）
        api_keyword = " ".join(keyword_list)

        self.logger.info(f"入力キーワード：{display_keyword}（API送信形式：{api_keyword}）")
        return display_keyword, api_keyword

    # -----------------------
    # 2つ目のフロー
    # 楽天APIで複数ページ検索して全商品を取得する
    # -----------------------
    def fetch_all_products(self, api_keyword: str, max_pages: int = 5) -> list[dict]:
        all_products: list[dict] = []

        for page in range(1, max_pages + 1):
            self.logger.info(f"楽天API検索中... {page}/{max_pages}ページ目")
            api_data = self.api.search(api_keyword, page=page)

            if api_data is None:
                self.logger.warning(f"{page}ページ目の取得に失敗しました。スキップします。")
                continue

            products = self.api.format_product_data(api_data)

            if not products:
                self.logger.info(f"{page}ページ目：商品なし。検索を終了します。")
                break

            self.logger.info(f"{page}ページ目：{len(products)}件取得")
            all_products.extend(products)

        self.logger.info(f"全ページ取得完了：合計{len(all_products)}件")
        return all_products

    # -----------------------
    # 3つ目のフロー
    # フィルタリング・並び替え・統計計算
    # -----------------------
    def process_products(self, raw_list: list[dict]) -> tuple[list[dict], dict]:
        # 中古・訳ありなどを除外
        filtered_list = self.builder.filter_list(raw_list)

        if not filtered_list:
            self.logger.warning("フィルタリング後、有効な商品がありませんでした。")
            return [], {}

        # 価格の安い順に並び替え
        sorted_list = self.builder.sort_by_price(filtered_list)

        # 統計計算（最安・平均・最高）
        summary = self.stats.get_price_summary(sorted_list)

        return sorted_list, summary

    # -----------------------
    # 4つ目のフロー
    # 結果を画面に表示する
    # -----------------------
    def print_result(self, display_keyword: str, sorted_list: list[dict], summary: dict) -> None:
        print("\n" + "="*50)
        print(f"  検索結果：{display_keyword}")
        print("="*50)

        if not sorted_list:
            print("該当商品が見つかりませんでした。")
            return

        print(f"有効ヒット件数：{len(sorted_list)}件")
        print(f"最安価格：{summary.get('min_price', '-'):,}円")
        print(f"平均価格：{summary.get('avr_price', '-'):,}円")
        print(f"最高価格：{summary.get('max_price', '-'):,}円")
        print("-"*50)
        print("▼ 上位10件（価格の安い順）")
        for i, product in enumerate(sorted_list[:10], start=1):
            print(f"  {i:>2}. {product['price']:>8,}円  {product['name'][:40]}")
        print("="*50)

    # -----------------------
    # 5つ目のフロー
    # CSVに保存する
    # -----------------------
    def save_csv(self, display_keyword: str, sorted_list: list[dict], summary: dict) -> None:
        filepath = self.csv_saver.save(
            keyword=display_keyword,
            summary=summary,
            product_list=sorted_list,
            count=len(sorted_list)
        )
        # 完了ポップアップ
        PopupManager.show_complete(filepath)

    # -----------------------
    # 全体を通して実行するメソッド
    # -----------------------
    def run_price_check(self) -> None:
        try:
            # ① キーワード入力
            display_keyword, api_keyword = self.input_keywords()

            # ② 楽天APIで検索（複数ページ）
            raw_list = self.fetch_all_products(api_keyword)

            if not raw_list:
                print("商品データを取得できませんでした。終了します。")
                return

            # ③ フィルタリング・並び替え・統計
            sorted_list, summary = self.process_products(raw_list)

            # ④ 結果を表示
            self.print_result(display_keyword, sorted_list, summary)

            if not sorted_list:
                return

            # ⑤ CSVに保存
            self.save_csv(display_keyword, sorted_list, summary)

        except ValueError as e:
            self.logger.error(f"入力エラー：{e}")
            PopupManager.show_error(str(e))
        except Exception as e:
            self.logger.error(f"予期せぬエラーが発生しました：{e}")
            PopupManager.show_error(f"予期せぬエラーが発生しました。\n\n{e}")
