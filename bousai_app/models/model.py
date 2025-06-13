import json
from config.config import DATA_FILE, HISTORY_FILE
from utils.utils import get_japan_time


class ShelterModel:
    """避難所データモデル"""
    
    def __init__(self):
        self.shelters = self.load_shelters()
    
    def load_shelters(self):
        """避難所データを読み込み"""
        try:
            with open(DATA_FILE, encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_shelters(self):
        """避難所データを保存"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.shelters, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def get_all_shelters(self):
        """全ての避難所を取得"""
        return self.shelters
    
    def get_shelters_by_district(self, district):
        """地区別に避難所を取得"""
        results = []
        for shelter in self.shelters:
            if shelter.get('district') == district:
                results.append(shelter)
        return results
    
    def add_shelter(self, shelter_data):
        """新しい避難所を追加"""
        shelter_data['id'] = len(self.shelters) + 1
        self.shelters.append(shelter_data)
        return self.save_shelters()
    
    def validate_shelter_data(self, name, district, address, latitude, longitude):
        """避難所データのバリデーション"""
        """ # 第5問：リスト
        # 以下のコードの2つの〇〇の中に、A~Dの中から適切なものを選んで貼り付けてください
        # ヒント：辞書を表現する記号は何ですか？
        # A) [,]
        # B) (,)
        # C) {,}
        # D) <,>
        # 必須項目チェック
        if not all([name, district, address, latitude, longitude]):
            return False, "必須項目が入力されていません。"        

        # 緯度経度の数値変換とバリデーション
        try:
            lat = float(latitude)
            lon = float(longitude)
            
            # 藤沢市周辺の座標範囲チェック (緯度: 35.2-35.5, 経度: 139.3-139.6)
            if not (35.2 <= lat <= 35.5) or not (139.3 <= lon <= 139.6):
                return False, "緯度・経度は藤沢市周辺の座標を入力してください。"
                
        except ValueError:
            return False, "緯度・経度は正しい数値で入力してください。"
        """ # 第5問：リスト
        
        return True, None


class NotificationModel:
    """通知履歴データモデル"""
    
    def __init__(self):
        self.history = self.load_history()
    
    def load_history(self):
        """履歴データを読み込み"""
        try:
            with open(HISTORY_FILE, encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_history(self):
        """履歴データを保存"""
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def get_all_history(self):
        """全ての履歴を取得"""
        return self.history
    
    def get_limited_history(self, limit=None):
        """制限付き履歴を取得"""
        if limit and limit > 0:
            return self.history[:limit]
        return self.history
    
    def add_warning_history(self, warnings_data):
        """警報・注意報の履歴を保存する"""
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
        if self.history:
            last_entry = self.history[0]
            # 警報・注意報の内容が同じ場合は保存しない
            last_warnings = set((w.get("name", ""), w.get("status", "")) for w in last_entry.get("warnings", []))
            current_warnings = set((w.get("name", ""), w.get("status", "")) for w in warnings_data.get("warnings", []))
            
            if last_warnings == current_warnings:
                return
        
        # 履歴の先頭に追加（最新が一番上）
        self.history.insert(0, history_entry)
        
        # 履歴は最大100件まで保持
        if len(self.history) > 100:
            self.history = self.history[:100]
        
        # ファイルに保存
        self.save_history() 