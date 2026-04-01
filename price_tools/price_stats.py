import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../")))
#自作
from utils.logger import SimpleLogger

###############################################
class PriceStats:
    def __init__(self):
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()
        
    # -----------------------
    # 1つ目のフロー
    # 最安値などの統計を計算する
    # データがない場合は空辞書を返す
    # -----------------------
    #引数名は共通にしてフィルター済みでも未処理でも並び替えれるようにしている
    def get_price_summary(self, product_data_list: list[dict]) -> dict:
        #データがない場合
        if not product_data_list:
            self.logger.info("統計計算対象の商品はありません")
            return {}
            
        self.logger.info("価格サマリーの作成を開始します")
        #平均計算用に価格だけのリストを作る->リスト内包表記
        prices = [item["price"] for item in product_data_list]
        
        #統計デーを計算して辞書にまとめる
        price_summary = {
            "min_price": min(prices),
            "max_price": max(prices),
            #//は切り捨てで結果を返す
            "avr_price": sum(prices) // len(prices),
        }
        self.logger.info(f"統計：最安値={price_summary['min_price']}円\n 平均={price_summary['avr_price']}円 \n 最高値={price_summary['max_price']}円 ")
        return price_summary
