##################################################
#APIリクエストをするため
import requests
#環境変数を使うための上旬ライブラリ
import os


#自作モジュール
from utils.logger import SimpleLogger
from utils.path_helper import get_env_path

from dotenv import load_dotenv 

#-----------------------
#.envの読み込み処理
#-----------------------
#path_helperを使って.envの特定して読込する
env_path = path_helper.get_env_path()
#load_dotenv()は（）内のpathを指定して、取り出す
load_dotenv(dotenv_path = env_path)

###################################################
# -----------------------
# 楽天APIクラス
# -----------------------
class RakutenAPI:
    def __init__(self):
        #logger
        self.logger_setup = SimpleLogger()
        self.logger = self.logger_setup.get_logger()
        
    #①楽天APIで商品検索を行う
    
    def search(self, product_name):
        self.logger.info(f"楽天API検索を開始します")
        
        #APIエンドポイント
        url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"