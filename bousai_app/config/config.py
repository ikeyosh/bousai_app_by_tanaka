# アプリケーション設定
import os

# 管理者認証情報
ADMIN_CREDENTIALS = {
    'admin': 'password123',
    'manager': 'shelter2025'
}

# 藤沢市の地区リスト
FUJISAWA_DISTRICTS = [
    "片瀬地区", "鵠沼地区", "辻堂地区", "村岡地区", "藤沢地区",
    "明治地区", "善行地区", "湘南大庭地区", "六会地区", "湘南台地区",
    "遠藤地区", "長後地区", "御所見地区"
]

# 気象警報・注意報設定
FUJISAWA_AREA_CODE = "1420500"  # 藤沢市のエリアコード

""" # 第1問：変数について学ぼう！
# 以下のコードの〇〇の中に、A~Dの中から適切なものを選んで貼り付けてください
# ヒント： URLは文字として扱う必要があります。文字を変数に入れるときは何で囲みますか？
# A) https://www.jma.go.jp/bosai/warning/data/warning/140000.json
# B) "https://www.jma.go.jp/bosai/warning/data/warning/140000.json"
# C) [https://www.jma.go.jp/bosai/warning/data/warning/140000.json]
# D) {https://www.jma.go.jp/bosai/warning/data/warning/140000.json}
# 解答例：WARNING_URL = "https://www.jma.go.jp/bosai/warning/data/warning/140000.json"
""" # 第1問：変数
WARNING_URL = ''

# ファイルパス
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'shelters.json')
HISTORY_FILE = os.path.join(BASE_DIR, 'data', 'notification_history.json')

# アプリケーション設定
SECRET_KEY = 'your-secret-key-here'
DEBUG = True
PORT = 5000 