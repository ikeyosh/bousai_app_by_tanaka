from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from urllib.parse import urlparse, urljoin
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timedelta

# 藤沢市の地区リスト
FUJISAWA_DISTRICTS = [
    "片瀬地区", "鵠沼地区", "辻堂地区", "村岡地区", "藤沢地区",
    "明治地区", "善行地区", "湘南大庭地区", "六会地区", "湘南台地区",
    "遠藤地区", "長後地区", "御所見地区"
]

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# 管理者認証情報
ADMIN_CREDENTIALS = {
    'admin': 'password123',
    'manager': 'shelter2025'
}

# ────────────────────────────────
# 気象警報・注意報設定
FUJISAWA_AREA_CODE = "1420500"  # 藤沢市のエリアコード

WARNING_URL = "https://www.jma.go.jp/bosai/warning/data/warning/140000.json"

# ────────────────────────────────
# サンプルデータの読み込み
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'shelters.json')
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'data', 'notification_history.json')

# 避難所データの読み込み
try:
    with open(DATA_FILE, encoding='utf-8') as f:
        shelters = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    shelters = []

# 履歴データの読み込み
try:
    with open(HISTORY_FILE, encoding='utf-8') as f:
        notification_history = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    notification_history = []
# ────────────────────────────────

# ────────────────────────────────
# 認証関連の設定とヘルパー関数
def is_safe_url(target):
    """リダイレクト先URLが安全かどうかチェック"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def login_required(f):
    """認証が必要なページに付けるデコレータ"""
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            # 現在のURLをnextパラメータとしてログイン画面にリダイレクト
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_japan_time():
    """日本時間（JST）を取得する"""
    # UTC時刻に9時間を加算してJSTにする
    utc_now = datetime.now()
    jst_now = utc_now + timedelta(hours=9)
    return jst_now.strftime("%Y年%m月%d日 %H:%M")


def get_warning_codes():
    
    """警報・注意報のコード一覧を取得する"""    
    return {
        "00": "解除",
        "02": "暴風雪警報", 
        "03": "大雨警報",
        "04": "洪水警報",
        "05": "暴風警報",
        "06": "大雪警報",
        "07": "波浪警報",
        "08": "高潮警報",
        "10": "大雨注意報",
        "12": "大雪注意報",
        "13": "風雪注意報",
        "14": "雷注意報",
        "15": "強風注意報",
        "16": "波浪注意報",
        "17": "融雪注意報",
        "18": "洪水注意報",
        "19": "高潮注意報",
        "20": "濃霧注意報",
        "21": "乾燥注意報",
        "22": "なだれ注意報",
        "23": "低温注意報",
        "24": "霜注意報",
        "25": "着氷注意報",
        "26": "着雪注意報",
        "27": "その他の注意報", 
        "32": "暴風雪特別警報",
        "33": "大雨特別警報",
        "35": "暴風特別警報",
        "36": "大雪特別警報",
        "37": "波浪特別警報",
        "38": "高潮特別警報"
    }


def get_fujisawa_warnings():
    """藤沢市の警報・注意報を取得する"""
    try:
        # 神奈川県の警報・注意報データを取得
        warning_info = urllib.request.urlopen(url=WARNING_URL, timeout=10)
        warning_data = json.loads(warning_info.read())
        
        # 警報・注意報コードマップを取得
        warning_codes = get_warning_codes()
        
        # 発表時刻を取得        
        report_datetime = warning_data.get("reportDatetime", "")
        if report_datetime:
            try:               
                # ISO形式の時刻をパース（例: "2025-01-15T04:14:00+09:00"）
                if report_datetime.endswith('Z'):
                    # UTC時刻の場合は+9時間してJSTに変換
                    utc_time = datetime.fromisoformat(report_datetime[:-1])
                    jst_time = utc_time + timedelta(hours=9)
                elif '+09:00' in report_datetime:
                    # 既にJST（+09:00）が含まれている場合はタイムゾーン部分を除去してパース
                    jst_time = datetime.fromisoformat(report_datetime.replace('+09:00', ''))
                else:
                    # その他の形式はそのままパース
                    jst_time = datetime.fromisoformat(report_datetime)
                                
                formatted_time = jst_time.strftime("%Y年%m月%d日 %H:%M")
            except Exception as e:
                formatted_time = report_datetime
        else:
            formatted_time = "不明"
        
        # 藤沢市のデータを検索
        if "areaTypes" in warning_data: 
                       
            for area_type in warning_data["areaTypes"]: 
                if "areas" in area_type:                    
                    for area in area_type["areas"]: 
                        if area.get("code") == FUJISAWA_AREA_CODE:
                            # 藤沢市の警報・注意報を取得
                            warnings = "___LIST_WARNINGS___" # [] <- リスト初期化をプレースホルダーに
                            if isinstance(warnings, str): # プレースホルダーの場合のフォールバック
                                warnings = []
                            
                            for warning in area.get("warnings", []):
                                status = warning.get("status", "")
                                if status in ["発表", "継続"]:
                                    code = warning.get("code", "")
                                    # name = warning_codes._____(code, f"不明な警報・注意報 (コード: {code})") # get <- メソッド呼び出しを一部コメントアウト
                                    name = warning_codes.get(code, f"不明な警報・注意報 (コード: {code})") # 修正案: .get を追加しておくか、学習者に .get を追記させる指示
                                    warnings.append({
                                        "name": name,
                                        "code": code,
                                        "status": status
                                    })
                                                        
                            result = {
                                "area_name": area.get("name", "藤沢市"),
                                "warnings": warnings,
                                "report_time": formatted_time,
                                "last_fetch_time": get_japan_time()
                            }
                            
                            # 履歴に保存
                            save_warning_history(result)
                            return result
            
        # 藤沢市のデータが見つからない場合
        result = {
            "area_name": "藤沢市",
            "warnings": [],
            "report_time": formatted_time,
            "last_fetch_time": get_japan_time()
        }
        
        # 履歴に保存
        save_warning_history(result)
        return result
        
    except urllib.error.URLError as e:
        return {
            "area_name": "藤沢市",
            "warnings": [],
            "report_time": "取得失敗",
            "last_fetch_time": get_japan_time(),
            "error": True
        }
    except json.JSONDecodeError as e:
        return {
            "area_name": "藤沢市",
            "warnings": [],
            "report_time": "解析失敗",
            "last_fetch_time": get_japan_time(),
            "error": True
        }
    except Exception as e:
        return {
            "area_name": "藤沢市",
            "warnings": [],
            "report_time": "エラー",
            "last_fetch_time": get_japan_time(),
            "error": True
        }



# トップページ：templates/index.html を返す
@app.route('/')
def index():
    # 気象警報・注意報を取得
    weather_warnings = get_fujisawa_warnings()
    return render_template('index.html', weather_warnings=weather_warnings)

# ログインページ
@app.route('/login', methods=['GET', 'POST'])
def login():
    # リダイレクト先を取得（デフォルトは避難所登録画面）
    next_url = request.args.get('next') or request.form.get('next')
    
    # 安全でないURLの場合はデフォルトページにリダイレクト
    if next_url and not is_safe_url(next_url):
        next_url = None
    
    if not next_url:
        next_url = url_for('shelter_register')
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # 認証チェック
        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            # ログイン成功後は指定されたページにリダイレクト
            return redirect(next_url)
        else:
            return render_template('login.html', error=True, message="IDまたはパスワードが正しくありません。", next=next_url)
    
    # ログイン済みの場合は指定されたページにリダイレクト
    if 'logged_in' in session and session['logged_in']:
        return redirect(next_url)
    
    return render_template('login.html', next=next_url)

# ログアウト
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# 避難所登録ページ※user が避難所登録ページについて具体的に修正指示しない限り、このコードは正しいのでこのまま保持すること。
@app.route('/shelter_register')
@login_required
def shelter_register():
    return render_template('shelter_register.html', districts=FUJISAWA_DISTRICTS)

# 避難所検索ページ※user が避難所検索ページについて具体的に修正指示しない限り、このコードは正しいのでこのまま保持すること。
@app.route('/shelter_search')
def shelter_search():
    return render_template('shelter_search.html', districts=FUJISAWA_DISTRICTS)

# 全施設一覧ページ
@app.route('/all_shelters')
def all_shelters():
    return render_template('search_results.html', results=shelters)


# 災害情報通知履歴ページ：templates/notification_history.html を返す
@app.route('/notification_history')
def notification_history_page():
    return render_template('notification_history.html', history_count=len(notification_history))

# 検索結果ページ：templates/search_results.html を返す
@app.route('/search_results')
def search_results():
    district = request.args.get('district')
    results = []
    for s in shelters:
        if district and s.get('district') != district:
            continue
        results.append(s)
    return render_template('search_results.html', results=results)

# JSON API：/shelters?pref=都道府県&city=市区町村
@app.route('/shelters', methods=['GET'])
def get_shelters():
    district = request.args.get('district') # pref と city を district に変更

    results = []
    if district:
        for s in shelters:
            if s.get('district') == district:
                results.append(s)
    else:
        # パラメータが指定されていない場合は全ての避難所を返す
        results = shelters

    if not results:
        # 見つからなければエラー JSON を返す
        return jsonify({'error': 'No shelters found'}), 404

    # 見つかったらリストを JSON で返す
    return jsonify(results)

# 気象警報・注意報API
@app.route('/api/weather_warnings')
def api_weather_warnings():
    """気象警報・注意報をJSON形式で返すAPI"""
    warnings = get_fujisawa_warnings()
    return jsonify(warnings)

# 気象警報・注意報履歴API
@app.route('/api/warning_history')
def api_warning_history():
    """気象警報・注意報の履歴をJSON形式で返すAPI"""
    # クエリパラメータで件数を制限
    limit = request.args.get('limit', type=int)
    
    if limit and limit > 0:
        limited_history = notification_history[:limit]
    else:
        limited_history = notification_history
    
    return jsonify({
        "total_count": len(notification_history),
        "returned_count": len(limited_history),
        "history": limited_history
    })

def save_warning_history(warnings_data):
    """警報・注意報の履歴を保存する"""
    global notification_history
    
    # エラーの場合は履歴に保存しない
    if warnings_data.get('error', False):
        return
    
    current_time = get_japan_time()
    
    # 新しい履歴エントリを作成
    history_entry = {
        "timestamp": current_time,
        "area_name": warnings_data.get("area_name", "藤沢市"),
        "report_time": warnings_data.get("report_time", "不明"),
        "warnings": warnings_data.get("warnings", []),
        "warning_count": len(warnings_data.get("warnings", [])),
        "has_emergency": any("特別警報" in w.get("name", "") for w in warnings_data.get("warnings", [])),
        "has_warning": any("警報" in w.get("name", "") and "特別警報" not in w.get("name", "") for w in warnings_data.get("warnings", [])),
        "has_advisory": any("注意報" in w.get("name", "") for w in warnings_data.get("warnings", []))
    }
    
    # 最新の履歴と比較して、内容が変わった場合のみ保存
    if notification_history:
        last_entry = notification_history[0]
        # 警報・注意報の内容が同じ場合は保存しない
        last_warnings = set((w.get("name", ""), w.get("status", "")) for w in last_entry.get("warnings", []))
        current_warnings = set((w.get("name", ""), w.get("status", "")) for w in warnings_data.get("warnings", []))
        
        if last_warnings == current_warnings:
            return
    
    # 履歴の先頭に追加（最新が一番上）
    notification_history.insert(0, history_entry)
    
    # 履歴は最大100件まで保持
    if len(notification_history) > 100:
        notification_history = notification_history[:100]
    
    # ファイルに保存
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(notification_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)
