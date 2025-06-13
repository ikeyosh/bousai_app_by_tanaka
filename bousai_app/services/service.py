import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from config.config import FUJISAWA_AREA_CODE, WARNING_URL
from utils.utils import get_japan_time
from models.model import NotificationModel


class WeatherService:
    """気象警報・注意報サービス"""
    
    def __init__(self):
        self.notification_model = NotificationModel()
    
    def get_warning_codes(self):
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
    
    def get_fujisawa_warnings(self):
        """藤沢市の警報・注意報を取得する"""
        try:
            # 神奈川県の警報・注意報データを取得
            warning_info = urllib.request.urlopen(url=WARNING_URL | '', timeout=10)
            warning_data = json.loads(warning_info.read())
            
            # 警報・注意報コードマップを取得
            warning_codes = self.get_warning_codes()
            
            # 発表時刻を取得        
            report_datetime = warning_data.get("reportDatetime", "")
            if report_datetime:
                try:
                    """ # 第2問：条件分岐について学ぼう！
                    # 以下のコードの〇〇の中に、A~Dの中から適切なものを選んで貼り付けてください
                    # A) elif
                    # B) else
                    # C) if
                    # D) while
                    # ヒント：「もし〜なら」を指す言葉。
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
                    """ # 第2問：条件分岐
                    
                    formatted_time = jst_time.strftime("%Y年%m月%d日 %H:%M")
                except Exception:
                    formatted_time = report_datetime
            else:
                formatted_time = "不明"
            
            # 藤沢市のデータを検索
            # 早期ガード：areaTypesが存在しない場合は処理を終了
            if "areaTypes" not in warning_data:
                result = {
                    "area_name": "藤沢市",
                    "warnings": [],
                    "report_time": formatted_time,
                    "last_fetch_time": get_japan_time()
                }
                self.notification_model.add_warning_history(result)
                return result
            
            for area_type in warning_data["areaTypes"]:
                # 早期ガード：areasが存在しない場合は次のループへ
                if "areas" not in area_type:
                    continue
                    
                for area in area_type["areas"]:
                    # 早期ガード：藤沢市のコードでない場合は次のループへ
                    if area.get("code") != FUJISAWA_AREA_CODE:
                        continue
                    
                    # 藤沢市の警報・注意報を取得
                    warnings = "___LIST_WARNINGS___"  # [] <- リスト初期化をプレースホルダーに
                    if isinstance(warnings, str):  # プレースホルダーの場合のフォールバック
                        warnings = []
                    
                    for warning in area.get("warnings", []):
                        status = warning.get("status", "")
                        # 早期ガード：発表・継続でない場合は次のループへ
                        if status not in ["発表", "継続"]:
                            continue
                            
                        code = warning.get("code", "")
                        # name = warning_codes._____(code, f"不明な警報・注意報 (コード: {code})") # get <- メソッド呼び出しを一部コメントアウト
                        name = warning_codes.get(code, f"不明な警報・注意報 (コード: {code})")  # 修正案: .get を追加しておくか、学習者に .get を追記させる指示
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
                    self.notification_model.add_warning_history(result)
                    return result
                
            # # 藤沢市のデータが見つからない場合
            # result = {
            #     "area_name": "藤沢市",
            #     "warnings": [],
            #     "report_time": formatted_time,
            #     "last_fetch_time": get_japan_time()
            # }
            
            # # 履歴に保存
            # self.notification_model.add_warning_history(result)
            # return result
            
        except urllib.error.URLError:
            return {
                "area_name": "藤沢市",
                "warnings": [],
                "report_time": "取得失敗",
                "last_fetch_time": get_japan_time(),
                "error": True
            }
        except json.JSONDecodeError:
            return {
                "area_name": "藤沢市",
                "warnings": [],
                "report_time": "解析失敗",
                "last_fetch_time": get_japan_time(),
                "error": True
            }
        except Exception:
            return {
                "area_name": "藤沢市",
                "warnings": [],
                "report_time": "エラー",
                "last_fetch_time": get_japan_time(),
                "error": True
            } 