from urllib.parse import urlparse, urljoin
from flask import request, session, redirect, url_for
from functools import wraps
from datetime import datetime, timedelta


def is_safe_url(target):
    """リダイレクト先URLが安全かどうかチェック"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def login_required(f):
    """認証が必要なページに付けるデコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            # 現在のURLをnextパラメータとしてログイン画面にリダイレクト
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_japan_time():
    """日本時間（JST）を取得する"""
    # UTC時刻に9時間を加算してJSTにする
    utc_now = datetime.now()
    jst_now = utc_now + timedelta(hours=9)
    return jst_now.strftime("%Y年%m月%d日 %H:%M") 