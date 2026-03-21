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
# -----------------------
# 楽天APIクラス
# 1つ目のフロー：APIへ接続 → キーワード検索
# -----------------------
class RakutenAPI:
    def __init__(self):
        #logger
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()
        
    #①楽天APIで商品検索を行う
    #型ヒントNoneの場合もあるため追加
    def search(self, product_name: str, page: int = 1) -> dict| None:
        self.logger.info(f"楽天API検索を開始します:{product_name}")
        
        #APIエンドポイント
        url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
        
        #リクエストパラメーターを渡す(何をお願いするか)
        #applicationID:楽天が決めている
        params = {
            "applicationId":os.getenv("RAKUTEN_API_ID"), #APIキー
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
        

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#実行してみる
if __name__ == "__main__":
    #インスタンス作成
    api = RakutenAPI()
    #テスト検索
    result = api.search("杜のすっぽん黒酢", page=1)
    
    if result:
        print("取得成功")
        print(type(result))
        
        items = result.get("Items",[])
        print(f"取得件数:{len(items)}")
        
        if items:
            print(items[0])
        else:
            print("取得失敗")