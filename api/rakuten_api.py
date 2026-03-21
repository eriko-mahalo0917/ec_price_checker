##################################################
#APIリクエストをするため
import requests
#環境変数を使うための上旬ライブラリ
import os
import sys

#自作モジュール
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from utils.logger import SimpleLogger
from utils.path_helper import get_env_path
#.envの読み込み
from dotenv import load_dotenv 

#-----------------------
#.envの読み込み処理
#-----------------------
#path_helperを使って.envの特定して読込する
env_path = get_env_path()
#load_dotenv()は（）内のpathを指定して、取り出す
load_dotenv(dotenv_path = env_path)

###################################################

class RakutenAPI:
    def __init__(self):
        #logger
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()
    
    # -----------------------
    # 1つ目のフロー   
    # 楽天APIにリクエストを送信し、
    # キーワード検索結果（商品データ）を取得する処理
    # -----------------------   
    #①楽天APIで商品検索を行う
    #型ヒントNoneの場合もあるため追加
    def search(self, product_name: str, page: int = 1) -> dict| None:
        self.logger.info(f"楽天API検索を開始します:{product_name}")
        
        #APIエンドポイント
        url = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20220601"
        
        #リクエストパラメーターを渡す(何をお願いするか)
        #applicationID:楽天が決めている
        params = {
            "applicationId":os.getenv("RAKUTEN_API_ID"), #APIキー
            "accessKey":os.getenv("RAKUTEN_ACCESS_KEY"),
            "keyword": product_name,                   #検索ワード
            "format":"json",
            "hits": 30,                                #取得件数(1回で最大30)
            "page": page                                  #ベージ番号はこの指定しているページのみ取得
        }
        
        try:
            #最大10秒待機！それ以上はタイムアウトでエラー ※timeout=10 はrequestsライブラリが持っている
            response = requests.get(url, params=params, timeout = 10)
            
            #ステータスコードチェックをする
            ## HTTPエラー（404や500）があれば例外を発生させる(止めるということ!)
            response.raise_for_status()
            #結果はjson形式受け取る
            rakuten_response = response.json()
            
            self.logger.info("楽天API検索に成功しました")
            return rakuten_response
        
        #通信系+HTTPエラー+タイムアウト全部拾える!
        except requests.exceptions.RequestException as e:
            self.logger.error(f"通信 or HTTPエラー:{e}")
            return None
        
    # -----------------------
    # 2つ目のフロー
    # 楽天APIのレスポンスから必要な商品情報だけを抽出する
    # -----------------------
    def format_product_data(self,api_data: dict)-> list[dict]:
        #商品情報を入れる空リスト
        product_data_list:list[dict] = []
        
        #「Items」を1件ずつループ処理
        #Itemがあればそれを使うが、なければ空リスト .get("Items", [])意味はなくてもOK
        for raw_item in api_data.get("Item",[]):
            #１つの商品のデータを取り出している
            product = raw_item["Item"]
            
            #必要な情報だけ辞書としてまとめる
            product_data = {
                #商品名
                "name": product["itemName"],
                #商品価格
                "price": product["itemPrice"],
                #商品ページURL
                "url": product["itemUrl"],
                #ショップ名
                "shop": product["shopName"],
                #平均レビュー（ない場合は０）
                "review_avg": product.get("reviewAverage", 0),
                #review件数（ない場合は０）
                "review_count": product.get("reviewCount", 0),
            }
            #リストに追加する
            product_data_list.append(product_data)
        
        return product_data_list 
        
        
        
        

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#実行してみる
if __name__ == "__main__":
    #インスタンス作成
    api = RakutenAPI()
    #-----------
    #1つ目のフロー
    #-----------
    result = api.search("杜のすっぽん黒酢", page=1)
    
    if result:
        print("取得成功")
        print(type(result))
        
        items = result.get("Items",[])
        print(f"取得件数:{len(items)}")
        
        if items:
            print(items[0])
    
            #-----------
            #2つ目のフロー
            #-----------
            formatted_data = api.format_product_data(result)
            print(f"整形後の件数:{len(formatted_data)}")
            if formatted_data:
                print("▼整形後データ（1件目）")
                print(formatted_data[0])
        else:
            print("整形データがありません")
    
    