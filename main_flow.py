#日本語フロー

#①main_flow.pyでrリサーチする商品名を入力する

#楽天APIで検索
#②api/rakuten_api.py
#for pageで回す（ページ制御）

#店舗・価格・URL抽出
#③price_tools/price_list_builder.py

#価格の統計で最安値・平均・最高金額
#④price_tools/price_stats.py

#自社価格と市場価格を比較
#⑤price_tools/self_vs_market.py

#CSVでデータを保存する
#⑥utils/csv_saver.py

#全体のフローを作成
#⑦main_flow.py

#実行
#⑧main.py