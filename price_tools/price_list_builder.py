import os
import sys
#(os.path.dirname(__file__),"../")は今いるフォルダの上の階層を指している
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../")))

#自作
from utils.logger import SimpleLogger

#configをimportして除外ワードを呼ぶ
from config import EXCLUDE_KEYWORDS

############################################

class PriceListBuilder:
    def __init__(self):
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()
    # -----------------------
    # 1つ目のフロー
    # 楽天のAPIから届いた商品リストを受取る
    # -----------------------
    def receive_product_data(self, product_data_list: list[dict]) -> list[dict]:
        self.logger.info(f"商品データを受け取りました：{len(product_data_list)}件")
        
        #受け取った商品をそのまま返す
        return product_data_list
    
    # -----------------------
    # ２つ目のフロー
    # 中古品などを除外するフィルタリングをする
    # -----------------------
    #リストの中から除外キーワードを含む商品を除外する(中古や訳ありなど) 
    def filter_list(self, product_data_list: list[dict]) ->list[dict]:
        self.logger.info(f"中古品などのキーワードが膨らまれる商品を除外します。除外キーワード：{EXCLUDE_KEYWORDS}")
        filtered_list = [
            product for product in product_data_list
            #product(商品1件)ごとにチェックする
            #if not any(...)は条件に合うものだけ残す※１つでもキーワードが入っていたらダメ
            #lower()は大文字小文字を無視
            #リスト内包表記：入れるもの for 取り出す元 if 条件
            if not any(keyword.lower() in product["name"].lower()
                    #除外キーワードを１つずつチェックしてね
                    for keyword in EXCLUDE_KEYWORDS)
        ]
        
        #除外された件数を計算
        removed_count = len(product_data_list) - len(filtered_list)
        self.logger.info(f"フィルタリング完了：{removed_count}件除外しました。残り：{len(filtered_list)}件")
        
        return filtered_list
        
    
    # -----------------------
    # ３つ目のフロー
    # 価格順に並び替える
    # -----------------------
    #引数名は共通にしてフィルター済みでも未処理でも並び替えれるようにしている
    def sort_by_price(self, product_data_list: list[dict]) -> list[dict]:
        self.logger.info("商品を価格順（安い順）へ並び替えます")
        #商品を価格の照準で並び替える
        #sorted()は並び替える関数　key = item:itemは１件ずつ取り出してそのpriceを使う
        #=lambdaは各priceを取り出すための無名関数
        sorted_list = sorted(product_data_list, key=lambda item: item["price"])
        self.logger.info("商品を価格順へ並び替えました")
        
        return sorted_list

    # -----------------------
    # 4つ目のフロー
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

    # -----------------------
    # 5つ目のフロー
    # 最終的なリストを返す
    # -----------------------
    def build_final_result(self, sorted_list: list[dict], price_summary:dict) ->dict:
        #並び替えしたリストと価格サマリーを１つのセットにしてまとめる
        self.logger.info("最終的な価格リストの構築をします")
        
        #２つのデータを１つの辞書にまとめる
        final_result = {
            "products": sorted_list, #中身list[dict]
            "summary": price_summary #中身dist
        }
        
        self.logger.info(f"リスト構築完了！合計{len(sorted_list)}件の商品が含まれています")
        
        return final_result
        


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# 実行してみる
if __name__ == "__main__":
    #テストデータ
    test_data = [
        {"name": "新品の高級時計", "price": 50000},
        {"name": "【中古】ボロボロの時計", "price": 5000},
        {"name": "ピカピカな新品時計", "price": 30000},
        {"name": "訳あり・箱なし時計", "price": 15000},
        {"name": "最新モデルの時計（新品）", "price": 45000},
    ]
    
    #インスタンス作成
    builder = PriceListBuilder()
    
    print("\n----１つ目のフロー：データを受け取り")
    row_list = builder.receive_product_data(test_data)
    
    print("\n----2つ目のフロー：除外する")
    filtered_list = builder.filter_list(row_list)
    
    print("\n----3つ目のフロー：並び替え（安い順）")
    sorted_list = builder.sort_by_price(filtered_list)

    print("\n----4つ目のフロー：統計フロー")
    summary = builder.get_price_summary(sorted_list)
    
    print("\n----5つ目のフロー：最終結果")
    final_result = builder.build_final_result(sorted_list, summary)
    print(f"最安値：{final_result["summary"].get("min_price")}円")
    print(f"商品数：{len(final_result['products'])}件")
    
    print("商品一覧：安い順")
    for p in final_result["products"]:
        #読みやすくしている
        print(f"- {p['price']}円: {p['name']}")