from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify
from config.config import ADMIN_CREDENTIALS, FUJISAWA_DISTRICTS
from utils.utils import is_safe_url, login_required
from models.model import ShelterModel, NotificationModel
from services.service import WeatherService

# Blueprintの作成
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
shelter_bp = Blueprint('shelter', __name__)
api_bp = Blueprint('api', __name__)


# ────────────────────────────────
# メインページ関連
# ────────────────────────────────

@main_bp.route('/')
def index():
    """トップページ"""
    weather_service = WeatherService()
    weather_warnings = weather_service.get_fujisawa_warnings()
    return render_template('index.html', weather_warnings=weather_warnings)


@main_bp.route('/notification_history')
def notification_history():
    """災害情報通知履歴ページ"""
    notification_model = NotificationModel()
    return render_template('notification_history.html', 
                         history_count=len(notification_model.get_all_history()))


# ────────────────────────────────
# 認証関連
# ────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """ログインページ"""
    # リダイレクト先を取得（デフォルトは避難所登録画面）
    next_url = request.args.get('next') or request.form.get('next')
    
    # 安全でないURLの場合はデフォルトページにリダイレクト
    if next_url and not is_safe_url(next_url):
        next_url = None
    
    if not next_url:
        next_url = url_for('shelter.shelter_register')
    
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


@auth_bp.route('/logout')
def logout():
    """ログアウト"""
    session.clear()
    return redirect(url_for('main.index'))


# ────────────────────────────────
# 避難所関連
# ────────────────────────────────

@shelter_bp.route('/shelter_search', methods=['GET', 'POST'])
def shelter_search():
    """避難所検索ページ"""
    shelter_model = ShelterModel()
    
    if request.method == 'POST':
        district = request.form.get('district', '').strip()

        # 地区が未入力の場合はエラー
        if not district:
            return render_template('shelter_search.html', error=True, message="地区を選択してください。", districts=FUJISAWA_DISTRICTS)

        results = []
        """ # 第3問：繰り返しについて学ぼう
         # 以下のコードの〇〇の中に、A~Dの中から適切なものを選んで貼り付けてください
         # ヒント：リストの中身を「一つずつ」取り出して処理したい場合に使うのは何ですか？
         # A) while
         # B) for
         # C) if
         # D) def
        for s in shelter_model.get_all_shelters():
            if district and s.get('district') != district:
                continue
            results.append(s)
        
        if not results:
            # 該当する避難所がない場合
            return render_template('shelter_search.html',
                                 error=True,
                                 message="該当する避難所がありません。",
                                 searched_district=district,
                                 districts=FUJISAWA_DISTRICTS)
        else:
            # 結果がある場合は検索結果ページへ
            return render_template('search_results.html', results=results, searched_district=district)
        """ # 第3問：繰り返し

    # GETリクエストの場合は通常のフォームを表示
    return render_template('shelter_search.html', districts=FUJISAWA_DISTRICTS)


@shelter_bp.route('/all_shelters')
def all_shelters():
    """全施設一覧ページ"""
    shelter_model = ShelterModel()
    return render_template('search_results.html', results=shelter_model.get_all_shelters())


@shelter_bp.route('/shelter_register', methods=['GET', 'POST'])
@login_required
def shelter_register():
    """避難所登録ページ（要認証）"""
    shelter_model = ShelterModel()
    
    if request.method == 'POST':
        # フォームデータを取得
        name = request.form.get('name', '').strip()
        district = request.form.get('district', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        facilities = request.form.get('facilities', '').strip()
        latitude = request.form.get('latitude', '').strip()
        longitude = request.form.get('longitude', '').strip()
        
        # チェックボックスの値を取得
        designated_shelter = bool(request.form.get('designated_shelter'))
        pet_space = bool(request.form.get('pet_space'))
        barrier_free_toilet = bool(request.form.get('barrier_free_toilet'))
        
        # バリデーション
        is_valid, error_message = shelter_model.validate_shelter_data(
            name, district, address, latitude, longitude)
        
        if not is_valid:
            return render_template('shelter_register.html', error=True, 
                                 message=error_message, districts=FUJISAWA_DISTRICTS)
            
        # 新しい避難所データを作成
        """ # 第4問：簡単な機能追加
        # 以下のコードの2つの〇〇の中に、A~Dの中から適切なものを選んで貼り付けてください
        # ヒント：辞書を表現する記号は何ですか？
        # A) [,]
        # B) (,)
        # C) {,}
        # D) <,>
        new_shelter = {
            'name': name,
            'pref': '神奈川県',
            'city': '藤沢市',
            'district': district,
            'address': address,  # ユーザー入力の住所部分のみ（神奈川県藤沢市は自動で付与される）
            'phone': phone if phone else '',
            'facilities': facilities if facilities else '',
            'designated_shelter': designated_shelter,
            'pet_space': pet_space,
            'barrier_free_toilet': barrier_free_toilet,
            'lat': float(latitude),  # 緯度を追加
            'lon': float(longitude)   # 経度を追加
        }
        """ # 第4問：辞書
        
        # データベースに保存
        if shelter_model.add_shelter(new_shelter):
            # 成功メッセージと共にページを表示
            return render_template('shelter_register.html', success=True, 
                                 message="避難所が登録されました！", districts=FUJISAWA_DISTRICTS)
        else:
            # エラーメッセージと共にページを表示
            return render_template('shelter_register.html', error=True, 
                                 message="登録中にエラーが発生しました", districts=FUJISAWA_DISTRICTS)
    
    # GETリクエストの場合は通常のフォームを表示
    return render_template('shelter_register.html', districts=FUJISAWA_DISTRICTS)


@shelter_bp.route('/search_results')
def search_results():
    """検索結果ページ"""
    shelter_model = ShelterModel()
    district = request.args.get('district')
    if district:
        results = shelter_model.get_shelters_by_district(district)
    else:
        results = shelter_model.get_all_shelters()
    return render_template('search_results.html', results=results)


# ────────────────────────────────
# API関連
# ────────────────────────────────

# Blueprintとしては@main_bpにしておくのが正しいが、今回は構造保持のため@api_bpにしている
# ※現在のBlueprint定義なら@api_bp以外はなんでも動く。
@main_bp.route('/shelters', methods=['GET'])
def get_shelters():
    """JSON API：/api/shelters?district=地区名"""
    shelter_model = ShelterModel()
    district = request.args.get('district')

    if district:
        results = shelter_model.get_shelters_by_district(district)
    else:
        # パラメータが指定されていない場合は全ての避難所を返す
        results = shelter_model.get_all_shelters()

    if not results:
        # 見つからなければエラー JSON を返す
        return jsonify({'error': 'No shelters found'}), 404

    # 見つかったらリストを JSON で返す
    return jsonify(results)


@api_bp.route('/weather_warnings')
def api_weather_warnings():
    """気象警報・注意報をJSON形式で返すAPI"""
    weather_service = WeatherService()
    warnings = weather_service.get_fujisawa_warnings()
    return jsonify(warnings)


@api_bp.route('/warning_history')
def api_warning_history():
    """気象警報・注意報の履歴をJSON形式で返すAPI"""
    notification_model = NotificationModel()
    
    # クエリパラメータで件数を制限
    limit = request.args.get('limit', type=int)
    
    limited_history = notification_model.get_limited_history(limit)
    
    return jsonify({
        "total_count": len(notification_model.get_all_history()),
        "returned_count": len(limited_history),
        "history": limited_history
    }) 