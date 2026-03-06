import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import pytz
import json
import os
import time
import requests
from collections import defaultdict
from PIL import Image
import re
import io

# 定数定義
GOLD_FUTURES_ADJUSTMENT = 29.0  # 先物とスポットの価格差

st.set_page_config(page_title="XAUUSD分析", page_icon="💰", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1d3a 25%, #0f1829 50%, #1e2139 75%, #0a0e27 100%);
        background-attachment: fixed;
    }
    
    .main .block-container {
        padding-top: 28rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    .sticky-header {
        position: fixed;
        top: 3.5rem;
        left: 0;
        right: 0;
        z-index: 9999;
        background: linear-gradient(135deg, #0a0e27 0%, #1a1d3a 100%);
        padding: 1rem 2rem 0.8rem 2rem;
        border-bottom: 2px solid rgba(0, 170, 255, 0.3);
        box-shadow: 0 4px 30px rgba(0, 170, 255, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .sticky-title {
        font-family: 'Orbitron', monospace;
        background: linear-gradient(90deg, #00aaff 0%, #0055ff 50%, #aa00ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900;
        font-size: 1.5rem;
        text-align: center;
        margin: 0;
        padding: 0;
        line-height: 1.2;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    .sticky-subtitle {
        font-family: 'Rajdhani', sans-serif;
        color: #8b9dc3;
        text-align: center;
        font-size: 0.6rem;
        margin: 0.2rem 0 0.6rem 0;
    }
    
    @media (max-width: 768px) {
        .sticky-header {
            top: 3rem;
        }
        .sticky-title {
            font-size: 1.1rem;
        }
        .sticky-subtitle {
            font-size: 0.5rem;
        }
        .main .block-container {
            padding-top: 30rem;
        }
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 5px #00aaff); }
        to { filter: drop-shadow(0 0 20px #0055ff); }
    }
    
        .stApp p, .stMarkdown p {
        font-family: 'Rajdhani', sans-serif !important;
        color: #c0d8ff !important;
    }
    
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', monospace !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #00aaff 0%, #0055ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 0.85rem !important;
        color: #8b9dc3 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 0.8rem !important;
    }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 85, 255, 0.1) 100%);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 0.8rem !important;
        border: 1px solid rgba(0, 170, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 170, 255, 0.2), inset 0 0 20px rgba(0, 170, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: rgba(0, 170, 255, 0.8);
        box-shadow: 0 8px 32px rgba(0, 170, 255, 0.4), inset 0 0 30px rgba(0, 170, 255, 0.2);
        transform: translateY(-3px);
    }
    
    .stSelectbox > div > div {
        background: rgba(10, 14, 39, 0.8) !important;
        border: 1px solid rgba(0, 170, 255, 0.4) !important;
        border-radius: 10px;
        color: #00aaff !important;
    }
    
    .stButton > button {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700;
        font-size: 1rem;
        background: linear-gradient(135deg, rgba(0, 170, 255, 0.2) 0%, rgba(0, 85, 255, 0.2) 100%);
        color: #00aaff !important;
        border: 2px solid #00aaff;
        border-radius: 12px;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 20px rgba(0, 170, 255, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00aaff 0%, #0055ff 100%);
        color: #ffffff !important;
        border-color: #ffffff;
        box-shadow: 0 0 40px rgba(0, 170, 255, 0.8), 0 0 60px rgba(0, 85, 255, 0.5);
        transform: translateY(-3px) scale(1.05);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1d3a 100%);
        border-right: 2px solid rgba(0, 170, 255, 0.3);
        box-shadow: 5px 0 30px rgba(0, 170, 255, 0.2);
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stCheckbox label,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: 'Rajdhani', sans-serif !important;
        color: #00aaff !important;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(0, 170, 255, 0.5);
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        font-family: 'Rajdhani', sans-serif !important;
        background: rgba(10, 14, 39, 0.8) !important;
        border: 1px solid rgba(0, 170, 255, 0.4) !important;
        border-radius: 10px;
        color: #00aaff !important;
        padding: 12px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #00aaff !important;
        box-shadow: 0 0 20px rgba(0, 170, 255, 0.5) !important;
    }
    
    .stRadio > div {
        background: rgba(10, 14, 39, 0.4);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(0, 170, 255, 0.2);
    }
    
    .stRadio label {
        color: #8b9dc3 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600;
    }
    
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #00aaff 50%, transparent 100%);
        margin: 2rem 0;
        box-shadow: 0 0 10px rgba(0, 170, 255, 0.5);
    }
    
    .streamlit-expanderHeader {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700;
        font-size: 1.2rem;
        background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 85, 255, 0.1) 100%);
        border: 1px solid rgba(0, 170, 255, 0.3);
        border-radius: 12px;
        color: #00aaff !important;
        backdrop-filter: blur(10px);
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #00aaff;
        box-shadow: 0 0 20px rgba(0, 170, 255, 0.4);
    }
.stExpander {
        margin-top: -2.9rem !important;
        margin-bottom: -0.5rem !important;
   }
    
    .stExpander .streamlit-expanderHeader {
        font-size: 0.1rem !important;
        background: transparent !important;
        color: #ff0000 !important;
        padding: 0.2rem 0.4rem !important;
        font-weight: 600 !important;
        margin-top: 0 !important;
        margin-bottom: 0rem !important;
    }

    div[data-testid="stExpander"] summary {
    background: transparent !important;
    }
    
    div[data-testid="stExpander"] details summary {
    background: transparent !important;
    }
    
    div[data-testid="stExpander"] details summary p {
    font-size: 0.8rem !important;
    }
    
    div[data-testid="stExpander"] details summary {
    font-size: 0.8rem !important;
    }
    
   .stExpander .streamlit-expanderContent {
    font-size: 0.13rem !important;
    color: #c0c0c0 !important;
    background: rgba(0, 170, 255, 0.15) !important;
    padding: 0.2rem 0.4rem !important;
    line-height: 1.3 !important;
    }

    .stExpander .streamlit-expanderContent p {
    font-size: 0.13rem !important;
    }
    
    .stExpander .streamlit-expanderContent div {
        font-size: 0.13rem !important;
    }
    
    .stExpander .streamlit-expanderContent * {
        font-size: 0.13rem !important;
    }

    .stAlert {
        background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 85, 255, 0.1) 100%);
        border-left: 4px solid #00aaff;
        border-radius: 12px;
        backdrop-filter: blur(10px);
        color: #8b9dc3 !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    .stMarkdown h2 {
        font-family: 'Orbitron', monospace !important;
        background: linear-gradient(90deg, #00aaff 0%, #0055ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        margin-top: 2rem;
    }
    
    .stMarkdown h3 {
        font-family: 'Rajdhani', sans-serif !important;
        color: #00aaff !important;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 170, 255, 0.3);
    }
    
    .stMarkdown h4 {
        font-family: 'Rajdhani', sans-serif !important;
        color: #8b9dc3 !important;
        font-weight: 600;
    }
    
    .stMarkdown ul {
        font-family: 'Rajdhani', sans-serif !important;
        color: #8b9dc3 !important;
    }
    
    .stMarkdown li::marker {
        color: #00aaff !important;
    }
    
    .stCaption {
        font-family: 'Rajdhani', sans-serif !important;
        color: #00aaff !important;
        text-shadow: 0 0 5px rgba(0, 170, 255, 0.3);
    }
    
    .stSpinner > div {
        border-top-color: #00aaff !important;
        border-right-color: #0055ff !important;
    }
    
    strong {
        color: #00aaff !important;
        font-weight: 700;
        text-shadow: 0 0 5px rgba(0, 170, 255, 0.3);
    }
    
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(10, 14, 39, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00aaff 0%, #0055ff 100%);
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 170, 255, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        box-shadow: 0 0 20px rgba(0, 170, 255, 0.8);
    }
    
    .stCheckbox {
        color: #00aaff !important;
    }
    
    .note-text {
        color: #8b9dc3;
        font-size: 0.75rem;
        margin-left: 1rem;
        margin-top: 0.2rem;
        display: block;
    }
</style>
""", unsafe_allow_html=True)

def check_password():
    def password_entered():
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == "4e42de48f9cdf95d8cbf5ad17f11a63601120eb1cdaa35eae088bb75196e4a67":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.markdown("# 🔒 XAUUSD分析アプリ")
        st.text_input("パスワード", type="password", on_change=password_entered, key="password", autocomplete="current-password")
        st.info("💡 パスワードを入力してください")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("# 🔒 XAUUSD分析アプリ")
        st.text_input("パスワード", type="password", on_change=password_entered, key="password", autocomplete="current-password")
        st.error("❌ パスワードが違います")
        return False
    return True

if not check_password():
    st.stop()

def save_rules_to_file(rules, username="default"):
    os.makedirs("user_data", exist_ok=True)
    with open(f"user_data/{username}_rules.json", "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)

def load_rules_from_file(username="default"):
    try:
        with open(f"user_data/{username}_rules.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_trades_to_file(trades, username="default", month=None):
    os.makedirs("user_data", exist_ok=True)
    if month:
        os.makedirs(f"user_data/archives/{month}", exist_ok=True)
        filepath = f"user_data/archives/{month}/trades.json"
    else:
        filepath = f"user_data/{username}_trades.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(trades, f, ensure_ascii=False, indent=2)

def load_trades_from_file(username="default", month=None):
    try:
        if month:
            filepath = f"user_data/archives/{month}/trades.json"
        else:
            filepath = f"user_data/{username}_trades.json"
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def get_archive_months():
    try:
        archive_path = "user_data/archives"
        if os.path.exists(archive_path):
            return sorted([d for d in os.listdir(archive_path) if os.path.isdir(os.path.join(archive_path, d))], reverse=True)
    except:
        pass
    return []

def archive_current_month(trades):
    if not trades:
        return False
    current_month = datetime.now().strftime("%Y-%m")
    save_trades_to_file(trades, month=current_month)
    return True

def resize_image_for_ocr(image, max_width=1920):
    """スマホスクショを適切なサイズにリサイズ"""
    width, height = image.size
    if width > max_width:
        ratio = max_width / width
        new_height = int(height * ratio)
        image = image.resize((max_width, new_height), Image.LANCZOS)
    return image

def extract_fxgt_trade_from_image(image):
    """FXGTのMT5スクショから取引情報を抽出（完全柔軟版）"""
    try:
        import easyocr
        import cv2
        import numpy as np
        
        # PILをnumpy配列に変換
        image_np = np.array(image)
        
        # スマホスクショ対応：リサイズ
        if image_np.shape[1] > 1920:
            ratio = 1920 / image_np.shape[1]
            new_width = 1920
            new_height = int(image_np.shape[0] * ratio)
            image_np = cv2.resize(image_np, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        
        # グレースケール変換
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_np
        
        # コントラスト強調
        gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=30)
        
        # ノイズ除去
        gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        reader = easyocr.Reader(['en'], gpu=False)
        result = reader.readtext(gray, detail=0)
        
        full_text = " ".join(result)
        
        print(f"=== OCR読み取り結果 ===")
        print(full_text)
        print(f"=====================")
        
        # タイプ（buy/sell）
        trade_type = "ロング" if "buy" in full_text.lower() else "ショート" if "sell" in full_text.lower() else "ロング"
        print(f"トレードタイプ: {trade_type}")
        
        # ロット数（0.01〜10.00の範囲の小数）
        lot = 0.01
        lot_pattern = r'\b(\d+\.\d{2})\b'
        lot_candidates = re.findall(lot_pattern, full_text)
        for candidate in lot_candidates:
            val = float(candidate)
            if 0.01 <= val <= 10.0:
                lot = val
                print(f"✅ ロット数: {lot}")
                break
        
        # エントリー価格・決済価格（4桁または5桁の小数）
        entry_price = 0
        exit_price = 0
        price_pattern = r'\b(\d{4,5}\.\d{1,2})\b'
        prices = re.findall(price_pattern, full_text)
        
        # 4桁・5桁の価格だけをフィルタ
        valid_prices = []
        for price in prices:
            val = float(price)
            if 1000 <= val <= 99999:  # 金価格の範囲
                valid_prices.append(val)
        
        if len(valid_prices) >= 2:
            entry_price = valid_prices[0]
            exit_price = valid_prices[1]
            print(f"✅ 価格: エントリー={entry_price}, 決済={exit_price}")
        
        # 日時抽出（柔軟な区切り文字対応）
        entry_date = datetime.now().strftime('%Y-%m-%d')
        entry_time = "00:00:00"
        exit_date = entry_date
        exit_time = "00:00:00"
        
        # パターン: 年.月.日 時,分.秒 または 年.月.日 時:分:秒 など
        # 区切り文字: . - / および : , .
        datetime_pattern = r'(\d{4})[.\-/](\d{2})[.\-/](\d{2})\s+(\d{2})[,:\.](\d{2})[,:\.](\d{2})'
        datetime_matches = re.findall(datetime_pattern, full_text)
        
        print(f"日時検出数: {len(datetime_matches)}")
        
        valid_datetimes = []
        for match in datetime_matches:
            year, month, day, hour, minute, second = match
            # バリデーション
            try:
                h, m, s = int(hour), int(minute), int(second)
                mo, d = int(month), int(day)
                
                if (0 <= h <= 23 and 0 <= m <= 59 and 0 <= s <= 59 and 
                    1 <= mo <= 12 and 1 <= d <= 31):
                    valid_datetimes.append({
                        'date': f"{year}-{month}-{day}",
                        'time': f"{hour}:{minute}:{second}"
                    })
                    print(f"✅ 有効な日時: {year}-{month}-{day} {hour}:{minute}:{second}")
                else:
                    print(f"❌ 無効な日時: {year}-{month}-{day} {hour}:{minute}:{second}")
            except ValueError:
                print(f"❌ 変換エラー: {match}")
        
        if len(valid_datetimes) >= 2:
            entry_date = valid_datetimes[0]['date']
            entry_time = valid_datetimes[0]['time']
            exit_date = valid_datetimes[1]['date']
            exit_time = valid_datetimes[1]['time']
            print(f"✅ 最終結果: エントリー={entry_date} {entry_time}, 決済={exit_date} {exit_time}")
        elif len(valid_datetimes) == 1:
            entry_date = valid_datetimes[0]['date']
            entry_time = valid_datetimes[0]['time']
            print(f"⚠️ エントリーのみ: {entry_date} {entry_time}")
        else:
            print("❌ 日時が検出できませんでした")
        
        return {
            'type': trade_type,
            'lot': lot,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'entry_date': entry_date,
            'entry_time': entry_time,
            'exit_date': exit_date,
            'exit_time': exit_time,
            'raw_text': full_text
        }
        
    except ImportError:
        return {
            'type': 'ロング',
            'lot': 0.01,
            'entry_price': 0,
            'exit_price': 0,
            'entry_date': datetime.now().strftime('%Y-%m-%d'),
            'entry_time': "00:00:00",
            'exit_date': datetime.now().strftime('%Y-%m-%d'),
            'exit_time': "00:00:00",
            'raw_text': 'OCRライブラリが利用できません。手動で入力してください。'
        }
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ エラー詳細: {error_detail}")
        return {
            'type': 'ロング',
            'lot': 0.01,
            'entry_price': 0,
            'exit_price': 0,
            'entry_date': datetime.now().strftime('%Y-%m-%d'),
            'entry_time': "00:00:00",
            'exit_date': datetime.now().strftime('%Y-%m-%d'),
            'exit_time': "00:00:00",
            'raw_text': f'エラー: {str(e)}'
        }

def calculate_trade_statistics(trades):
    if not trades:
        return None
    
    total = len(trades)
    wins = 0
    losses = 0
    total_profit = 0
    total_loss = 0
    
    emotion_stats = defaultdict(lambda: {'wins': 0, 'total': 0})
    
    # トレード日数を計算
    trade_dates = [trade['date'] for trade in trades]
    unique_dates = set(trade_dates)
    total_days = len(unique_dates)
    
    print(f"=== 統計計算デバッグ ===")
    print(f"総トレード数: {total}")
    print(f"トレード日数: {total_days}")
    
    for i, trade in enumerate(trades):
        # 価格差を計算
        if trade['type'] == "ロング":
            price_diff = trade['exit_price'] - trade['entry_price']
        else:
            price_diff = trade['entry_price'] - trade['exit_price']
        
        # ロット数を考慮（金の場合、0.01ロット = 100オンス = 1ドルの価格差で100ドルの損益）
        lot_size = trade.get('lot_size', 0.01)
        pnl = price_diff * lot_size * 100  # 金の場合の係数
        
        print(f"トレード{i+1}: タイプ={trade['type']}, エントリー={trade['entry_price']}, 決済={trade['exit_price']}, ロット={lot_size}, 損益=${pnl:.2f}")
        
        if pnl > 0:
            wins += 1
            total_profit += pnl
        elif pnl < 0:
            losses += 1
            total_loss += abs(pnl)
        else:
            # 損益が0の場合もカウント（引き分け）
            print(f"  ⚠️ 損益が0です")
        
        emotion = trade.get('emotion', '不明')
        emotion_stats[emotion]['total'] += 1
        if pnl > 0:
            emotion_stats[emotion]['wins'] += 1
    
    print(f"勝ち: {wins}, 負け: {losses}")
    print(f"総利益: ${total_profit:.2f}, 総損失: ${total_loss:.2f}")
    
    win_rate = (wins / total * 100) if total > 0 else 0
    avg_profit = (total_profit / wins) if wins > 0 else 0
    avg_loss = (total_loss / losses) if losses > 0 else 0
    profit_factor = (total_profit / total_loss) if total_loss > 0 else 0
    net_profit = total_profit - total_loss
    
    # 1日平均トレード数
    trades_per_day = total / total_days if total_days > 0 else 0
    
    print(f"勝率: {win_rate:.1f}%")
    print(f"純利益: ${net_profit:.2f}")
    print(f"プロフィットファクター: {profit_factor:.2f}")
    print(f"======================")
    
    return {
        'total': total,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
        'avg_profit': avg_profit,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'net_profit': net_profit,
        'total_profit': total_profit,
        'total_loss': total_loss,
        'emotion_stats': dict(emotion_stats),
        'total_days': total_days,
        'trades_per_day': trades_per_day
    }
def generate_harsh_feedback(stats):
    if not stats:
        return "データ不足。最低10トレードは記録してください。"
    
    feedback = "## 🔴 あなたの弱点\n\n"
    has_weakness = False
    
    # 1. サンプル不足チェック
    if stats['total'] < 10:
        remaining = 10 - stats['total']
        feedback += f"""⚠️ **データ不足**

トレード記録を始めたばかりですね！現在{stats['total']}回のデータがあります。

統計的に信頼できる分析を行うには、最低10回、できれば20回以上のデータが必要です。もう少しトレードを重ねると、あなたの勝ちパターンや改善点がはっきり見えてきます。

焦らず、コツコツ記録を続けてください。

✨ あと{remaining}回で詳細な分析が可能になります！
🎯 目標：まずは10回の記録を目指しましょう！

---

"""
        has_weakness = True
    
    # 2. 勝率とPFのバランス評価
    if stats['win_rate'] < 40 and stats['profit_factor'] < 1.0:
        feedback += "- **勝率も利益率も低い状態です。**\n\n  エントリータイミングと損切り・利確の両方を見直す必要があります。根本的な改善が必要です。\n"
        has_weakness = True
    elif stats['win_rate'] > 60 and stats['profit_factor'] < 1.5:
        feedback += "- **勝率は高いですが、利益が小さいです。**\n\n  利確を早くしすぎています。トレンドに乗り続ける練習をしてください。小さな利益で満足せず、大きく伸ばすことを意識しましょう。\n"
        has_weakness = True
    elif stats['win_rate'] < 50 and stats['profit_factor'] < 1.0:
        feedback += "- **勝率が低く、トータルで負けています。**\n\n  トレード手法が間違っている可能性が高い。このまま続けると資金を失います。今すぐ見直してください。\n"
        has_weakness = True
    
    # 3. 損益バランス
    if stats['avg_loss'] > stats['avg_profit']:
        feedback += "- **損大利小になっています。**\n\n  損切りが遅すぎる、または利確が早すぎる。トレーダーとして致命的な欠陥です。損切りは早く、利確は遅く。\n"
        has_weakness = True
    
    if stats['avg_loss'] > stats['avg_profit'] * 2:
        feedback += "- **損切りが遅すぎます。**\n\n  ナンピン（負けを取り戻そうとさらにポジションを持つ）していませんか？損失を先延ばしにすると、さらに傷口が広がります。\n"
        has_weakness = True
    
    # 4. プロフィットファクター
    if stats['profit_factor'] < 1:
        feedback += "- **プロフィットファクター1未満。トータルで負けています。**\n\n  このままでは破産確定です。今すぐトレードを止めて見直してください。\n"
        has_weakness = True
    elif stats['profit_factor'] < 1.5:
        feedback += "- **プロフィットファクターが低すぎます。**\n\n  ギリギリ勝っているだけ。安定して勝てていません。\n"
        has_weakness = True
    
    # 5. 感情的トレード
    emotion_issues = []
    for emotion, data in stats['emotion_stats'].items():
        if emotion in ['焦り', '不安', '興奮'] and data['total'] > 0:
            wr = (data['wins'] / data['total'] * 100) if data['total'] > 0 else 0
            if wr < 50:
                emotion_issues.append(f"{emotion}（勝率{wr:.0f}%）")
    
    if emotion_issues:
        feedback += f"- **感情的なトレードで負けています: {', '.join(emotion_issues)}。**\n\n  メンタルコントロールができていない。冷静さを完全に欠いています。\n"
        has_weakness = True
    
    # 6. オーバートレード（1日平均15回以上）
    if stats['total_days'] >= 3 and stats['trades_per_day'] >= 15:
        feedback += f"- **1日平均{stats['trades_per_day']:.1f}回トレードしています。オーバートレードの可能性があります。**\n\n  質より量になっていませんか？厳選したチャンスだけを狙いましょう。無理にトレードする必要はありません。\n"
        has_weakness = True
    
    if not has_weakness and stats['total'] >= 10:
        feedback = "## ✅ 現時点で大きな弱点は見つかりませんでした\n\n引き続き冷静なトレードを心がけてください。\n\n"
    
    return feedback

def generate_advice(stats):
    if not stats:
        return ""
    
    advice = "## 💡 改善のためのアドバイス\n\n"
    
    # 勝率は低いが利益率は良い
    if stats['win_rate'] < 50 and stats['profit_factor'] > 1.5:
        advice += "- 勝率は低いですが、利益率が高いです。**損小利大の理想的なトレードができています。** 方向性は間違っていません。この調子で続けてください。エントリー精度を少し上げることに集中すれば、さらに良くなります。\n"
    
    # 勝率も利益率も良い
    if stats['win_rate'] > 60 and stats['profit_factor'] > 2.0:
        advice += "- 勝率・利益率ともに優秀です。**現在の手法を維持してください。** 無理に変える必要はありません。\n"
    
    # 平均損失と利益のバランスが良い
    if stats['avg_profit'] > stats['avg_loss'] * 1.5:
        advice += "- 利益が損失の1.5倍以上あります。**損小利大が実現できています。** 素晴らしいリスク管理です。\n"
    
    # 冷静な時の勝率が高い
    for emotion, data in stats['emotion_stats'].items():
        if emotion == '冷静' and data['total'] > 0:
            wr = (data['wins'] / data['total'] * 100) if data['total'] > 0 else 0
            if wr > 60:
                advice += f"- **「冷静」な時の勝率が{wr:.0f}%と高い。** 感情的にならないことが成功の鍵です。このマインドを維持してください。\n"
    
    advice += "\n### 🎯 推奨アクション\n"
    advice += "- エントリー前に必ず損切り価格を決める\n"
    advice += "- 利確は2段階に分ける（50%ずつ）\n"
    advice += "- 連続3回負けたら必ず休憩する\n"
    advice += "- トレード記録を毎回つける（継続できています！）\n"
    
    return advice

if "trade_rules" not in st.session_state:
    st.session_state.trade_rules = load_rules_from_file()

if "trade_history" not in st.session_state:
    st.session_state.trade_history = load_trades_from_file()

if "selected_trades" not in st.session_state:
    st.session_state.selected_trades = []

if "current_price" not in st.session_state:
    st.session_state.current_price = 0
    st.session_state.price_change = 0
    st.session_state.price_pct = 0
    st.session_state.rsi_value = 0
    st.session_state.rsi_status = "-"
    st.session_state.support_value = 0
    st.session_state.resistance_value = 0

if "ocr_data" not in st.session_state:
    st.session_state.ocr_data = None

st.markdown(f'''
<div class="sticky-header">
    <div class="sticky-title">XAUUSD<br>リアルタイム分析アシスタント</div>
    <div class="sticky-subtitle">マルチタイムフレーム対応版 - 高精度戦略</div>
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.3rem; margin-top: 0.3rem;">
        <div style="background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 85, 255, 0.1) 100%); border: 1px solid rgba(0, 170, 255, 0.3); border-radius: 8px; padding: 0.2rem; text-align: center;">
            <div style="font-size: 0.75rem; color: #8b9dc3; margin-bottom: 0.05rem; line-height: 1;">🔽 サポート</div>
            <div style="font-size: 1.2rem; font-weight: bold; background: linear-gradient(135deg, #00aaff 0%, #0055ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1;">${st.session_state.support_value:,.0f}</div>
        </div>
        <div style="background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 85, 255, 0.1) 100%); border: 1px solid rgba(0, 170, 255, 0.3); border-radius: 8px; padding: 0.2rem; text-align: center;">
            <div style="font-size: 0.75rem; color: #8b9dc3; margin-bottom: 0.05rem; line-height: 1;">💰 現在価格</div>
            <div style="font-size: 1.2rem; font-weight: bold; background: linear-gradient(135deg, #00aaff 0%, #0055ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1;">${st.session_state.current_price:,.2f}</div>
            <div style="font-size: 0.4rem; color: #8b9dc3; line-height: 1;">{st.session_state.price_change:+.2f} ({st.session_state.price_pct:+.2f}%)</div>
        </div>
        <div style="background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 85, 255, 0.1) 100%); border: 1px solid rgba(0, 170, 255, 0.3); border-radius: 8px; padding: 0.2rem; text-align: center;">
            <div style="font-size: 0.75rem; color: #8b9dc3; margin-bottom: 0.05rem; line-height: 1;">🔼 レジスタンス</div>
            <div style="font-size: 1.2rem; font-weight: bold; background: linear-gradient(135deg, #00aaff 0%, #0055ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1;">${st.session_state.resistance_value:,.0f}</div>
        </div>
        <div style="background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 85, 255, 0.1) 100%); border: 1px solid rgba(0, 170, 255, 0.3); border-radius: 8px; padding: 0.2rem; text-align: center;">
            <div style="font-size: 0.75rem; color: #8b9dc3; margin-bottom: 0.05rem; line-height: 1;">📈 RSI (7)</div>
            <div style="font-size: 1.2rem; font-weight: bold; background: linear-gradient(135deg, #00aaff 0%, #0055ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1;">{st.session_state.rsi_value:.1f}</div>
            <div style="font-size: 0.4rem; color: #8b9dc3; line-height: 1;">{st.session_state.rsi_status}</div>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

st.sidebar.header("⚙️ 設定")

timeframe_options = {
    "1分足": ("1m", "2d"),  # 1d → 2d に変更
    "15分足": ("15m", "5d"),
    "30分足": ("30m", "5d"),
    "1時間足": ("1h", "1mo"),
    "4時間足": ("1h", "3mo"),
    "日足": ("1d", "6mo"),
    "週足": ("1wk", "1y")
}

selected_timeframe = st.sidebar.selectbox("時間足", list(timeframe_options.keys()), index=3)
interval, period = timeframe_options[selected_timeframe]

trade_style = st.sidebar.radio("トレードスタイル", ["スキャルピング", "デイトレード", "スイングトレード"], index=1)

st.sidebar.markdown("---")
st.sidebar.header("🔄 自動更新設定")
auto_refresh = st.sidebar.checkbox("自動更新を有効化（30秒間隔）", value=False)
refresh_interval = 30  # 30秒固定

st.sidebar.markdown("---")
st.sidebar.header("📝 マイトレードルール")

new_rule = st.sidebar.text_input("新しいルールを追加", placeholder="例: 損失が2%に達したら取引停止")
if st.sidebar.button("➕ ルール追加"):
    if new_rule and new_rule not in st.session_state.trade_rules:
        st.session_state.trade_rules.append(new_rule)
        save_rules_to_file(st.session_state.trade_rules)
        st.sidebar.success("✅ ルールを追加しました")
        st.rerun()

if st.session_state.trade_rules:
    st.sidebar.markdown("### 現在のルール:")
    for idx, rule in enumerate(st.session_state.trade_rules):
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            st.sidebar.write(f"✓ {rule}")
        with col2:
            if st.sidebar.button("🗑️", key=f"del_{idx}"):
                st.session_state.trade_rules.pop(idx)
                save_rules_to_file(st.session_state.trade_rules)
                st.rerun()

@st.cache_data(ttl=30)
def get_realtime_gold_price():
    try:
        ticker = yf.Ticker("GC=F")
        latest = ticker.history(period="1d", interval="1m")
        if len(latest) > 0:
            return latest['Close'].iloc[-1] - GOLD_FUTURES_ADJUSTMENT
    except:
        pass
    
    return None

@st.cache_data(ttl=60)
def get_gold_data(period, interval):
    try:
        ticker = yf.Ticker("GC=F")
        data = ticker.history(period=period, interval=interval)
        
        if len(data) > 0:
            if data.index.tz is None:
                data.index = data.index.tz_localize('UTC')
            data.index = data.index.tz_convert('Asia/Tokyo')
            
            # 先物価格からスポット価格相当に補正
            data['Open'] = data['Open'] - GOLD_FUTURES_ADJUSTMENT
            data['High'] = data['High'] - GOLD_FUTURES_ADJUSTMENT
            data['Low'] = data['Low'] - GOLD_FUTURES_ADJUSTMENT
            data['Close'] = data['Close'] - GOLD_FUTURES_ADJUSTMENT
        
        return data
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return None

def create_mobile_friendly_chart(df, current, support, resistance, pivot, selected_timeframe):
    """モバイル完全対応のシンプルチャート"""
    import json
    
    # ローソク足データ
    candles = []
    for idx, row in df.iterrows():
        candles.append({
            'time': idx.strftime('%Y-%m-%d %H:%M'),
            'open': float(row['Open']),
            'high': float(row['High']),
            'low': float(row['Low']),
            'close': float(row['Close'])
        })
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ background: #0a0e27; touch-action: pan-x pan-y; }}
            #chart {{ width: 100%; height: 600px; }}
        </style>
    </head>
    <body>
        <div id="chart"></div>
        <script>
            const candleData = {json.dumps(candles)};
            
            const options = {{
                series: [{{
                    name: 'XAUUSD',
                    data: candleData.map(c => ({{
                        x: new Date(c.time),
                        y: [c.open, c.high, c.low, c.close]
                    }}))
                }}],
                chart: {{
                    type: 'candlestick',
                    height: 600,
                    background: '#0a0e27',
                    foreColor: '#8b9dc3',
                    zoom: {{
                        enabled: true,
                        type: 'x',
                        autoScaleYaxis: true
                    }},
                    toolbar: {{
                        show: true,
                        tools: {{
                            zoom: true,
                            zoomin: true,
                            zoomout: true,
                            pan: true,
                            reset: true
                        }}
                    }}
                }},
                plotOptions: {{
                    candlestick: {{
                        colors: {{
                            upward: '#00aaff',
                            downward: '#aa00ff'
                        }}
                    }}
                }},
                xaxis: {{
                    type: 'datetime',
                    labels: {{
                        style: {{ colors: '#8b9dc3' }}
                    }}
                }},
                yaxis: {{
                    tooltip: {{ enabled: true }},
                    labels: {{
                        style: {{ colors: '#8b9dc3' }},
                        formatter: function(value) {{
                            return value.toFixed(2);
                        }}
                    }}
                }},
                grid: {{
                    borderColor: '#2a2e39'
                }},
                annotations: {{
                    yaxis: [
                        {{
                            y: {support},
                            borderColor: '#00ff88',
                            label: {{
                                text: 'サポート',
                                position: 'left',
                                style: {{ color: '#fff', background: '#00ff88' }}
                            }}
                        }},
                        {{
                            y: {resistance},
                            borderColor: '#ff0088',
                            label: {{
                                text: 'レジスタンス',
                                position: 'left',
                                style: {{ color: '#fff', background: '#ff0088' }}
                            }}
                        }},
                        {{
                            y: {pivot},
                            borderColor: '#ffaa00',
                            label: {{
                                text: 'ピボット',
                                position: 'left',
                                style: {{ color: '#fff', background: '#ffaa00' }}
                            }}
                        }}
                    ]
                }}
            
            const chart = new ApexCharts(document.querySelector("#chart"), options);
            chart.render();
        </script>
    </body>
    </html>
    """
    return html

def create_lightweight_chart(df, current, support, resistance, pivot, r1, s1, selected_timeframe):
    """Lightweight Charts (TradingView) でチャートを生成"""
    
    # データをJSON形式に変換
    candlestick_data = []
    for index, row in df.iterrows():
        candlestick_data.append({
            'time': int(index.timestamp()),
            'open': float(row['Open']),
            'high': float(row['High']),
            'low': float(row['Low']),
            'close': float(row['Close'])
        })
    
    # SMA20データ
    sma20_data = []
    for index, row in df.iterrows():
        if not pd.isna(row.get('SMA_20')):
            sma20_data.append({
                'time': int(index.timestamp()),
                'value': float(row['SMA_20'])
            })
    
    # SMA50データ
    sma50_data = []
    if 'SMA_50' in df.columns:
        for index, row in df.iterrows():
            if not pd.isna(row.get('SMA_50')):
                sma50_data.append({
                    'time': int(index.timestamp()),
                    'value': float(row['SMA_50'])
                })
    
    import json
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
        <style>
            body {{ margin: 0; padding: 0; background: #0a0e27; }}
            #chart {{ width: 100%; height: 600px; }}
        </style>
    </head>
    <body>
        <div id="chart"></div>
        <script>
            const chart = LightweightCharts.createChart(document.getElementById('chart'), {{
                layout: {{
                    background: {{ color: '#0a0e27' }},
                    textColor: '#8b9dc3',
                }},
                grid: {{
                    vertLines: {{ color: 'rgba(42, 46, 57, 0.5)' }},
                    horzLines: {{ color: 'rgba(42, 46, 57, 0.5)' }},
                }},
                crosshair: {{
                    mode: LightweightCharts.CrosshairMode.Normal,
                }},
                rightPriceScale: {{
                    borderColor: 'rgba(197, 203, 206, 0.8)',
                }},
                timeScale: {{
                    borderColor: 'rgba(197, 203, 206, 0.8)',
                    timeVisible: true,
                    secondsVisible: false,
                }},
                handleScroll: {{
                    mouseWheel: true,
                    pressedMouseMove: true,
                    horzTouchDrag: true,
                    vertTouchDrag: true,
                }},
                handleScale: {{
                    axisPressedMouseMove: true,
                    mouseWheel: true,
                    pinch: true,
                }},
            }});

            const candlestickSeries = chart.addCandlestickSeries({{
                upColor: '#00aaff',
                downColor: '#aa00ff',
                borderUpColor: '#00aaff',
                borderDownColor: '#aa00ff',
                wickUpColor: '#00aaff',
                wickDownColor: '#aa00ff',
            }});

            candlestickSeries.setData({json.dumps(candlestick_data)});

            const sma20Series = chart.addLineSeries({{
                color: '#00aaff',
                lineWidth: 2,
                title: 'SMA20',
            }});
            sma20Series.setData({json.dumps(sma20_data)});

            {f'''
            const sma50Series = chart.addLineSeries({{
                color: '#0055ff',
                lineWidth: 2,
                title: 'SMA50',
            }});
            sma50Series.setData({json.dumps(sma50_data)});
            ''' if sma50_data else ''}

            // サポート・レジスタンスライン
            candlestickSeries.createPriceLine({{
                price: {support},
                color: '#00ff88',
                lineWidth: 1,
                lineStyle: LightweightCharts.LineStyle.Dashed,
                axisLabelVisible: true,
                title: 'サポート',
            }});

            candlestickSeries.createPriceLine({{
                price: {resistance},
                color: '#ff0088',
                lineWidth: 1,
                lineStyle: LightweightCharts.LineStyle.Dashed,
                axisLabelVisible: true,
                title: 'レジスタンス',
            }});

            candlestickSeries.createPriceLine({{
                price: {pivot},
                color: '#ffaa00',
                lineWidth: 1,
                lineStyle: LightweightCharts.LineStyle.Dotted,
                axisLabelVisible: true,
                title: 'ピボット',
            }});

            chart.timeScale().fitContent();
        </script>
    </body>
    </html>
    """
    
    return html_code
    
@st.cache_data(ttl=60)
def calculate_advanced_technicals(data):
    df = data.copy()
    
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=7).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df['ATR'] = true_range.rolling(14).mean()
    
    df['Pivot'] = (df['High'].shift(1) + df['Low'].shift(1) + df['Close'].shift(1)) / 3
    df['R1'] = 2 * df['Pivot'] - df['Low'].shift(1)
    df['S1'] = 2 * df['Pivot'] - df['High'].shift(1)
    
    return df

def find_support_resistance(data):
    recent = data.tail(100)
    resistance = recent['High'].rolling(20).max().iloc[-1]
    support = recent['Low'].rolling(20).min().iloc[-1]
    return support, resistance

def calculate_targets_with_atr(current, atr, support, resistance):
    long_entry = support + (resistance - support) * 0.2
    long_sl = current - (atr * 1.5)
    long_tp1 = current + (atr * 2)
    long_tp2 = current + (atr * 3)
    
    short_entry = resistance - (resistance - support) * 0.2
    short_sl = current + (atr * 1.5)
    short_tp1 = current - (atr * 2)
    short_tp2 = current - (atr * 3)
    
    return {
        'long': {'entry': long_entry, 'sl': long_sl, 'tp1': long_tp1, 'tp2': long_tp2},
        'short': {'entry': short_entry, 'sl': short_sl, 'tp1': short_tp1, 'tp2': short_tp2}
    }

def generate_advanced_analysis(style, current, change_pct, rsi, macd, macd_signal, atr, support, resistance, pivot, r1, s1, timeframe):
    targets = calculate_targets_with_atr(current, atr, support, resistance)
    
    macd_trend = "🟢 買いシグナル" if macd > macd_signal else "🔴 売りシグナル"
    
    rr_long = (targets['long']['tp2'] - targets['long']['entry']) / (targets['long']['entry'] - targets['long']['sl']) if (targets['long']['entry'] - targets['long']['sl']) != 0 else 0
    rr_short = (targets['short']['entry'] - targets['short']['tp2']) / (targets['short']['sl'] - targets['short']['entry']) if (targets['short']['sl'] - targets['short']['entry']) != 0 else 0
    
    if style == "スキャルピング":
        analysis = f"""
## 💨 スキャルピング分析（{timeframe}）

### 📊 テクニカル状況

- **現在価格**: ${current:,.2f} ({change_pct:+.2f}%)"""
        
        st.markdown(analysis)

        st.markdown('<style>.stExpander .streamlit-expanderHeader {font-size: 0.3rem !important;}</style>', unsafe_allow_html=True)
        with st.expander("ℹ️ 用語解説", expanded=False):
            st.markdown('<div style="font-size: 0.7rem; color: #d0d0d0; padding: 0.2rem 0.5rem; margin-top: -1.5rem;">現在価格の変動率 - プラス（+）: 前の時間帯より上昇 → 上昇トレンドの可能性が高い / マイナス（-）: 前の時間帯より下落 → 下落トレンドの可能性が高い</div>', unsafe_allow_html=True)
        
        analysis2 = f"""
- RSI (7): {rsi:.1f} {"⚠️ 買われすぎ" if rsi > 70 else "✅ 売られすぎ" if rsi < 30 else "➡️ 中立"}"""
        
        st.markdown(analysis2)

        st.markdown('<style>.stExpander .streamlit-expanderHeader {font-size: 0.3rem !important;}</style>', unsafe_allow_html=True)
        with st.expander("ℹ️ 用語解説", expanded=False):
            st.markdown('<div style="font-size: 0.7rem; color: #d0d0d0; padding: 0.2rem 0.5rem; margin-top: -1.5rem;">RSI (7) - 70以上: 買われすぎ → 売りを検討 / 30以下: 売られすぎ → 買いを検討 / 40-60: 中立 → トレンドに従って判断</div>', unsafe_allow_html=True)
        
        analysis3 = f"""
- MACD: {macd_trend}"""
        
        st.markdown(analysis3)

        st.markdown('<style>.stExpander .streamlit-expanderHeader {font-size: 0.3rem !important;}</style>', unsafe_allow_html=True)
        with st.expander("ℹ️ 用語解説", expanded=False):
            st.markdown('<div style="font-size: 0.7rem; color: #d0d0d0; padding: 0.2rem 0.5rem; margin-top: -1.5rem;">MACD - 🟢 買いシグナル: MACDラインがシグナルラインを上抜け → 上昇トレンドの始まり / 🔴 売りシグナル: MACDラインがシグナルラインを下抜け → 下落トレンドの始まり</div>', unsafe_allow_html=True)
     
        analysis4 = f"""
- ATR: {atr:.2f}（ボラティリティ指標）"""
        
        st.markdown(analysis4)

        st.markdown('<style>.stExpander .streamlit-expanderHeader {font-size: 0.3rem !important;}</style>', unsafe_allow_html=True)
        with st.expander("ℹ️ 用語解説", expanded=False):
            st.markdown('<div style="font-size: 0.7rem; color: #d0d0d0; padding: 0.2rem 0.5rem; margin-top: -1.5rem;">ATR（ボラティリティ指標） - ボラティリティ（価格変動の大きさ）を測る指標 / 数値が大きい: 値動きが激しい → 損切り幅を広くする / 数値が小さい: 値動きが穏やか → 通常の戦略で対応</div>', unsafe_allow_html=True)
        
        analysis5 = f"""
- ピボット: ${pivot:,.2f}"""
        
        st.markdown(analysis5)

        st.markdown('<style>.stExpander .streamlit-expanderHeader {font-size: 0.3rem !important;}</style>', unsafe_allow_html=True)
        with st.expander("ℹ️ 用語解説", expanded=False):
            st.markdown('<div style="font-size: 0.7rem; color: #d0d0d0; padding: 0.2rem 0.5rem; margin-top: -1.5rem;">ピボットポイント - 前日の高値・安値・終値から計算される基準価格。トレーダーが注目するポイント / S1（サポート1）: 第1サポートライン（下値支持） / R1（レジスタンス1）: 第1レジスタンスライン（上値抵抗）</div>', unsafe_allow_html=True)
        
        analysis6 = f"""
### 🎯 高精度エントリー戦略

#### 🟢 ロングの場合
**エントリー条件：**
- 価格が ${s1:,.2f}（S1）〜${pivot:,.2f}（ピボット）で反発
- RSI < 40 かつ MACD上昇転換
- ATRベースの最適タイミング

**ポジション詳細：**
- **エントリー**: ${targets['long']['entry']:,.2f}
- **損切り（SL）**: ${targets['long']['sl']:,.2f}（ATR 1.5倍）
- **利確1（50%）**: ${targets['long']['tp1']:,.2f}（ATR 2倍）
- **利確2（50%）**: ${targets['long']['tp2']:,.2f}（ATR 3倍）
- **リスクリワード**: 1:{rr_long:.2f}

#### 🔴 ショートの場合
**エントリー条件：**
- 価格が ${pivot:,.2f}（ピボット）〜${r1:,.2f}（R1）で反落
- RSI > 60 かつ MACD下降転換
- ATRベースの最適タイミング

**ポジション詳細：**
- **エントリー**: ${targets['short']['entry']:,.2f}
- **損切り（SL）**: ${targets['short']['sl']:,.2f}（ATR 1.5倍）
- **利確1（50%）**: ${targets['short']['tp1']:,.2f}（ATR 2倍）
- **利確2（50%）**: ${targets['short']['tp2']:,.2f}（ATR 3倍）
- **リスクリワード**: 1:{rr_short:.2f}

### ⚠️ 注意点

- **スプレッド考慮：エントリーは±3ドルの余裕を持つ**
<small class="note-text">→ ブローカーのスプレッドは2-5ドル程度。エントリー価格から±3ドルの範囲で約定されることを想定</small>

- **経済指標30分前は避ける**
<small class="note-text">→ 雇用統計、GDP、FOMC発表などの重要指標前後は価格が急変動。Investing.comで経済カレンダーを確認</small>

- **連続3回負けたら1時間休憩必須**
<small class="note-text">→ コンビニまで歩いてみる、一旦画面から離れる、画面をオフにする、深呼吸する</small>

- **ATRが平均の1.5倍以上の時は見送り**
<small class="note-text">→ 通常ATRが10-15の場合、22以上なら見送り。ボラティリティが高すぎて損切りに引っかかりやすい</small>
"""
        st.markdown(analysis6, unsafe_allow_html=True)
    
    elif style == "デイトレード":
        analysis = f"""
## 📊 デイトレード分析（{timeframe}）

### 📈 市場環境分析

- 現在価格: ${current:,.2f} ({change_pct:+.2f}%)
- RSI (7): {rsi:.1f}
- MACD: {macd_trend}
- ATR: {atr:.2f}
- ピボットポイント: ${pivot:,.2f}
- レジスタンス: R1=${r1:,.2f}
- サポート: S1=${s1:,.2f}

### トレンド判定
{"📈 **強い上昇トレンド** - ロング優勢" if change_pct > 0.5 and macd > macd_signal else "📉 **強い下落トレンド** - ショート優勢" if change_pct < -0.5 and macd < macd_signal else "➡️ **レンジ相場** - ブレイクアウト待ち"}

### 🎯 精密トレード戦略

#### 🟢 ロングの場合
**最適エントリーゾーン：**
- ${s1:,.2f}〜${targets['long']['entry']:,.2f}
- サポートでの反発確認後

**段階的利確プラン：**
- **第1目標（30%）**: ${targets['long']['tp1']:,.2f}
- **第2目標（40%）**: ${pivot + atr:,.2f}
- **第3目標（30%）**: ${targets['long']['tp2']:,.2f}

**リスク管理：**
- **損切り**: ${targets['long']['sl']:,.2f}
- **最大許容損失**: 資金の1%以下
- **リスクリワード**: 1:{rr_long:.2f}

#### 🔴 ショートの場合
**最適エントリーゾーン：**
- ${targets['short']['entry']:,.2f}〜${r1:,.2f}
- レジスタンスでの反落確認後

**段階的利確プラン：**
- **第1目標（30%）**: ${targets['short']['tp1']:,.2f}
- **第2目標（40%）**: ${pivot - atr:,.2f}
- **第3目標（30%）**: ${targets['short']['tp2']:,.2f}

**リスク管理：**
- **損切り**: ${targets['short']['sl']:,.2f}
- **最大許容損失**: 資金の1%以下
- **リスクリワード**: 1:{rr_short:.2f}

### ⏰ 時間帯別戦略
- **9:00-12:00（東京）**: トレンドフォロー、ボラティリティ低
- **16:00-19:00（欧州）**: ブレイクアウト狙い、ボラティリティ増加
- **22:00-02:00（NY）**: メインセッション、最も活発

### 📊 当日の注意点
- {"RSI買われすぎ、利確検討" if rsi > 70 else "RSI売られすぎ、押し目買い検討" if rsi < 30 else "RSI中立、トレンドに従う"}
- ATRが{atr:.2f}なので、{"ボラティリティ高め、損切り幅を拡大" if atr > 15 else "ボラティリティ通常、標準的戦略で"}
- ポジションは必ず当日中に決済
"""
        st.markdown(analysis)
    
    else:
        analysis = f"""
## 📈 スイングトレード分析（{timeframe}）

### 🌍 マクロ環境
- **現在価格**: ${current:,.2f} ({change_pct:+.2f}%)
- **週次トレンド**: {"上昇" if change_pct > 1 else "下降" if change_pct < -1 else "中立"}
- **RSI (7)**: {rsi:.1f}
- **MACD**: {macd_trend}

### 大局的トレンド分析
{"🟢 **強気相場継続中** - 押し目買い戦略" if change_pct > 1.0 and macd > macd_signal else "🔴 **弱気相場継続中** - 戻り売り戦略" if change_pct < -1.0 and macd < macd_signal else "🟡 **調整局面** - レンジブレイク待ち"}

### 🎯 中期ポジション戦略

#### 🟢 ロングポジション
**エントリー戦略：**
- **最適ゾーン**: ${s1:,.2f}〜${support:,.2f}
- **分割エントリー**: 3回に分けて建玉
  - 1回目（40%）: ${support:,.2f}
  - 2回目（30%）: ${s1:,.2f}
  - 3回目（30%）: ${s1 - atr:,.2f}

**利確プラン（3段階）：**
- **第1目標（30%）**: ${pivot + atr * 2:,.0f}
- **第2目標（40%）**: ${r1:,.0f}
- **第3目標（30%）**: ${r1 + atr * 2:,.0f}

**損切り：**
- **絶対SL**: ${targets['long']['sl']:,.0f}
- **トレーリングストップ**: 価格が${pivot:,.0f}突破後、ピボット-ATRに引き上げ

**想定保有期間**: 3日〜2週間

#### 🔴 ショートポジション
**エントリー戦略：**
- **最適ゾーン**: ${resistance:,.2f}〜${r1:,.2f}
- **分割エントリー**: 3回に分けて建玉
  - 1回目（40%）: ${resistance:,.2f}
  - 2回目（30%）: ${r1:,.2f}
  - 3回目（30%）: ${r1 + atr:,.2f}

**利確プラン（3段階）：**
- **第1目標（30%）**: ${pivot - atr * 2:,.0f}
- **第2目標（40%）**: ${s1:,.0f}
- **第3目標（30%）**: ${s1 - atr * 2:,.0f}

**損切り：**
- **絶対SL**: ${targets['short']['sl']:,.0f}
- **トレーリングストップ**: 価格が${pivot:,.0f}下抜け後、ピボット+ATRに引き下げ

**想定保有期間**: 3日〜2週間

### 🌐 ファンダメンタル要因
- 地政学リスク（中東情勢）→ 金価格上昇要因
- FRB政策（利上げ観測）→ 金価格下落要因
- インフレ率→ 金需要に影響
- ドル相場→ 逆相関関係

### 📅 今週の重要イベント
- 経済指標発表日をチェック
- FOMC議事録
- 雇用統計

### ⚠️ リスク管理
- ポジションサイズ: 資金の2〜5%
- 週末リスク: 金曜夕方までに50%利確検討
- ニュースチェック: 毎日2回（朝・夕）必須
"""
        st.markdown(analysis)

def display_trade_rules():
    if st.session_state.trade_rules:
        st.markdown("### 📋 あなたのトレードルール")
        for idx, rule in enumerate(st.session_state.trade_rules, 1):
            st.markdown(f"**{idx}.** {rule}")
    else:
        st.info("💡 左サイドバーから自分のトレードルールを追加できます")

try:
    with st.spinner(f'📊 {selected_timeframe}データを取得中...'):
        realtime_price = get_realtime_gold_price()
        data = get_gold_data(period, interval)
        
        if data is None or len(data) == 0:
            st.error("❌ データ取得失敗")
            st.stop()
        
        df = calculate_advanced_technicals(data)
    
    if realtime_price:
        current = realtime_price
        previous = data['Close'].iloc[-2]
    else:
        current = data['Close'].iloc[-1]
        previous = data['Close'].iloc[-2]
    
    change = current - previous
    pct = (change / previous) * 100
    rsi = df['RSI'].iloc[-1]
    macd = df['MACD'].iloc[-1]
    macd_signal = df['Signal'].iloc[-1]
    atr = df['ATR'].iloc[-1]
    support, resistance = find_support_resistance(df)
    pivot = df['Pivot'].iloc[-1]
    r1 = df['R1'].iloc[-1]
    s1 = df['S1'].iloc[-1]
    
    st.session_state.current_price = current
    st.session_state.price_change = change
    st.session_state.price_pct = pct
    st.session_state.rsi_value = rsi
    st.session_state.rsi_status = "買われすぎ" if rsi > 70 else "売られすぎ" if rsi < 30 else "中立"
    st.session_state.support_value = support
    st.session_state.resistance_value = resistance
    
    jst = pytz.timezone('Asia/Tokyo')
    now_jst = datetime.now(jst)
    latest_data_time = df.index[-1]
    time_diff_minutes = (now_jst - latest_data_time).total_seconds() / 60
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='XAUUSD',
        increasing_line_color='#00aaff',
        decreasing_line_color='#aa00ff'
    ))
    
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA20', line=dict(color='#00aaff', width=2)))
    if len(df) >= 50:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA50', line=dict(color='#0055ff', width=2)))
    
    fig.add_hline(y=support, line_dash="dash", line_color="#00ff88", annotation_text="サポート")
    fig.add_hline(y=resistance, line_dash="dash", line_color="#ff0088", annotation_text="レジスタンス")
    fig.add_hline(y=pivot, line_dash="dot", line_color="#ffaa00", annotation_text="ピボット")
    
    fig.update_layout(
    title=f'📈 XAUUSD {selected_timeframe}チャート (JST)',
    height=600,
    xaxis_rangeslider_visible=False,
    xaxis_title='時刻 (JST)',
    template='plotly_dark',
    paper_bgcolor='rgba(10,14,39,0.8)',
    plot_bgcolor='rgba(10,14,39,0.5)',
    font=dict(family='Rajdhani', color='#8b9dc3')
    )
    
    fig.update_xaxes(
    tickformat='%m/%d<br>%H:%M',
    )

    st.markdown("<br>" * 5, unsafe_allow_html=True)
    
    # モバイル対応チャート
    import streamlit.components.v1 as components
    mobile_chart_html = create_mobile_friendly_chart(df, current, support, resistance, pivot, selected_timeframe)
    components.html(mobile_chart_html, height=650, scrolling=False)

    # 更新ボタンをチャート直後に配置
    col_update, col_space = st.columns([1, 3])
    with col_update:
        if st.button("🔄 今すぐ更新"):
            st.cache_data.clear()
            st.rerun()
    st.caption(f"💡 価格表示について：先物価格（GC=F）から{GOLD_FUTURES_ADJUSTMENT:.0f}ドル補正してスポット価格相当を表示しています")
    st.caption(f"⏰ チャート最終データ: {latest_data_time.strftime('%Y年%m月%d日 %H:%M')} JST（約{time_diff_minutes:.0f}分前）")
    
    st.markdown("---")
    
    analysis_options = {
        "選択中": trade_style,
        "スキャルピング": "スキャルピング",
        "デイトレード": "デイトレード",
        "スイングトレード": "スイングトレード"
    }
    
    selected_analysis = st.selectbox("📊 分析タイプ", list(analysis_options.keys()), index=0)
    display_style = analysis_options[selected_analysis]
    
    generate_advanced_analysis(display_style, current, pct, rsi, macd, macd_signal, atr, support, resistance, pivot, r1, s1, selected_timeframe)
    
    st.markdown("---")
    display_trade_rules()
    
    st.markdown("---")
    st.header("📝 トレード記録")
    
    tab1, tab2, tab3, tab4 = st.tabs(["記録追加", "📸 画像で追加", "記録管理", "統計分析"])
    
    with tab1:
        with st.expander("新しいトレードを記録", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                trade_date = st.date_input("日時")
                trade_type = st.selectbox("タイプ", ["ロング", "ショート"])
                entry_price = st.number_input("エントリー価格", value=float(current), format="%.2f")
                exit_price = st.number_input("決済価格", value=float(current + 50 if trade_type == "ロング" else current - 50), format="%.2f")
            
            with col2:
                lot_size = st.number_input("ロット数", value=0.01, format="%.2f")
                entry_reason = st.text_area("エントリー理由", placeholder="例: RSI30で反発")
                exit_reason = st.text_area("決済理由", placeholder="例: 利確目標到達")
                emotion = st.selectbox("感情", ["冷静", "焦り", "自信", "不安", "興奮"])
            
            if st.button("💾 記録を保存"):
                trade_data = {
                    'date': str(trade_date),
                    'type': trade_type,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'lot_size': lot_size,
                    'entry_reason': entry_reason,
                    'exit_reason': exit_reason,
                    'emotion': emotion
                }
                
                st.session_state.trade_history.append(trade_data)
                save_trades_to_file(st.session_state.trade_history)
                st.success("✅ トレード記録を保存しました")
                st.rerun()
    
    with tab2:
        st.markdown("### 📸 MT5スクショから自動入力")
        
        st.info("""
💡 **画像アップロードのヒント**

**最も精度が高い画像：**
- FXGT MT5のトレード詳細画面（スマホスクショOK！）
- スクリーンショット（スマホ：音量下+電源ボタン / PC：Win + Shift + S / Cmd + Shift + 4）
- PNG形式推奨

**精度を上げるコツ：**
✅ MT5のトレード詳細画面だけを切り取る
✅ 文字が鮮明に見える明るさ
✅ エントリー価格 → 決済価格の形式
❌ 画面が暗い、ボケている
❌ 複数のウィンドウが重なっている

**読み取れる情報：**
- トレードタイプ（buy → ロング、sell → ショート）
- エントリー価格・決済価格
- ロット数
- エントリー・決済の日時（MT5表示時刻そのまま）
""")
        
        uploaded_file = st.file_uploader("画像をアップロード（最大10MB）", type=['png', 'jpg', 'jpeg'], key="ocr_upload")
        
        if uploaded_file is not None:
            # ファイルサイズチェック
            if uploaded_file.size > 10 * 1024 * 1024:
                st.error("❌ ファイルサイズが10MBを超えています。画像を圧縮してください。")
            else:
                image = Image.open(uploaded_file)
                
                col_img, col_result = st.columns([1, 1])
                
                with col_img:
                    st.image(image, caption="アップロードされた画像", use_container_width=True)
                
                with col_result:
                    if st.button("🔍 画像から情報を抽出"):
                        with st.spinner("画像を解析中..."):
                            ocr_result = extract_fxgt_trade_from_image(image)
                            st.session_state.ocr_data = ocr_result
                            
                            if ocr_result['entry_price'] > 0:
                                st.success("✅ 抽出完了！")
                                st.markdown(f"**トレードタイプ**: {ocr_result['type']}")
                                st.markdown(f"**ロット**: {ocr_result['lot']}")
                                st.markdown(f"**エントリー**: ${ocr_result['entry_price']:,.2f}")
                                st.markdown(f"**決済**: ${ocr_result['exit_price']:,.2f}")
                                st.markdown(f"**エントリー日時**: {ocr_result['entry_date']} {ocr_result['entry_time']}")
                                st.markdown(f"**決済日時**: {ocr_result['exit_date']} {ocr_result['exit_time']}")
                            else:
                                st.warning("⚠️ 価格情報を抽出できませんでした。手動で入力してください。")
                                with st.expander("デバッグ情報", expanded=False):
                                    st.text(ocr_result['raw_text'])
        
        if st.session_state.ocr_data is not None:
            st.markdown("---")
            st.markdown("### 📝 抽出データを確認・修正")
            
            ocr_col1, ocr_col2 = st.columns(2)
            
            with ocr_col1:
                ocr_trade_date = st.date_input("日付", value=datetime.strptime(st.session_state.ocr_data['entry_date'], '%Y-%m-%d') if st.session_state.ocr_data['entry_date'] else datetime.now(), key="ocr_date")
                ocr_entry_time = st.text_input("エントリー時刻（MT5表示）", value=st.session_state.ocr_data['entry_time'], key="ocr_entry_time")
                ocr_exit_time = st.text_input("決済時刻（MT5表示）", value=st.session_state.ocr_data['exit_time'], key="ocr_exit_time")
                ocr_trade_type = st.selectbox("タイプ", ["ロング", "ショート"], 
                                              index=0 if st.session_state.ocr_data['type'] == "ロング" else 1, 
                                              key="ocr_type")
                
                ocr_entry = st.number_input("エントリー価格", 
                                            value=float(st.session_state.ocr_data['entry_price']) if st.session_state.ocr_data['entry_price'] > 0 else 5000.0, 
                                            format="%.2f", key="ocr_entry")
                ocr_exit = st.number_input("決済価格", 
                                          value=float(st.session_state.ocr_data['exit_price']) if st.session_state.ocr_data['exit_price'] > 0 else 5050.0, 
                                          format="%.2f", key="ocr_exit")
            
            with ocr_col2:
                ocr_lot = st.number_input("ロット数", 
                                         value=float(st.session_state.ocr_data['lot']), 
                                         format="%.2f", key="ocr_lot")
                
                ocr_entry_reason = st.text_area("エントリー理由", placeholder="例: RSI30で反発", key="ocr_reason_entry")
                ocr_exit_reason = st.text_area("決済理由", placeholder="例: 利確目標到達", key="ocr_reason_exit")
                ocr_emotion = st.selectbox("感情", ["冷静", "焦り", "自信", "不安", "興奮"], key="ocr_emotion")
            
            if st.button("💾 OCRデータを保存", key="save_ocr"):
                trade_data = {
                    'date': str(ocr_trade_date),
                    'entry_time': ocr_entry_time,
                    'exit_time': ocr_exit_time,
                    'type': ocr_trade_type,
                    'entry_price': ocr_entry,
                    'exit_price': ocr_exit,
                    'lot_size': ocr_lot,
                    'entry_reason': ocr_entry_reason,
                    'exit_reason': ocr_exit_reason,
                    'emotion': ocr_emotion
                }
                
                st.session_state.trade_history.append(trade_data)
                save_trades_to_file(st.session_state.trade_history)
                st.session_state.ocr_data = None
                st.success("✅ トレード記録を保存しました")
                st.rerun()
    
    with tab3:
        if st.session_state.trade_history:
            st.markdown(f"### 📚 トレード記録（{len(st.session_state.trade_history)}件）")
            
            col_a, col_b, col_c = st.columns([2, 2, 2])
            with col_a:
                if st.button("📦 今月をアーカイブ"):
                    if archive_current_month(st.session_state.trade_history):
                        st.session_state.trade_history = []
                        save_trades_to_file(st.session_state.trade_history)
                        st.success("✅ アーカイブしました")
                        st.rerun()
            
            with col_b:
                if st.button("🗑️ 選択削除"):
                    if st.session_state.selected_trades:
                        st.session_state.trade_history = [t for i, t in enumerate(st.session_state.trade_history) if i not in st.session_state.selected_trades]
                        save_trades_to_file(st.session_state.trade_history)
                        st.session_state.selected_trades = []
                        st.success("✅ 削除しました")
                        st.rerun()
            
            with col_c:
                if st.button("⚠️ 全削除"):
                    st.session_state.show_delete_confirm = True
            
            if 'show_delete_confirm' in st.session_state and st.session_state.show_delete_confirm:
                st.warning("⚠️ 本当に全て削除しますか？この操作は取り消せません。")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("はい、削除します"):
                        st.session_state.trade_history = []
                        save_trades_to_file(st.session_state.trade_history)
                        st.session_state.show_delete_confirm = False
                        st.success("✅ 全て削除しました")
                        st.rerun()
                with col_no:
                    if st.button("いいえ、キャンセル"):
                        st.session_state.show_delete_confirm = False
                        st.rerun()
            
            for idx, trade in enumerate(st.session_state.trade_history[-20:]):
                pnl = (trade['exit_price'] - trade['entry_price']) if trade['type'] == "ロング" else (trade['entry_price'] - trade['exit_price'])
                col_check, col_info = st.columns([1, 9])
                with col_check:
                    if st.checkbox("", key=f"trade_{idx}"):
                        if idx not in st.session_state.selected_trades:
                            st.session_state.selected_trades.append(idx)
                with col_info:
                    time_info = f" {trade.get('entry_time', '')} - {trade.get('exit_time', '')}" if 'entry_time' in trade else ""
                    st.markdown(f"**{trade['date']}{time_info}** - {trade['type']} - 損益: ${pnl:.2f}")
            
            archive_months = get_archive_months()
            if archive_months:
                st.markdown("### 📁 アーカイブ")
                selected_month = st.selectbox("月を選択", archive_months)
                if st.button("表示"):
                    archived_trades = load_trades_from_file(month=selected_month)
                    if archived_trades:
                        for trade in archived_trades:
                            pnl = (trade['exit_price'] - trade['entry_price']) if trade['type'] == "ロング" else (trade['entry_price'] - trade['exit_price'])
                            time_info = f" {trade.get('entry_time', '')} - {trade.get('exit_time', '')}" if 'entry_time' in trade else ""
                            st.markdown(f"**{trade['date']}{time_info}** - {trade['type']} - ${pnl:.2f}")
        else:
            st.info("トレード記録がありません")
    
    with tab4:
        if st.session_state.trade_history:
            stats = calculate_trade_statistics(st.session_state.trade_history)
            
            if stats:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("勝率", f"{stats['win_rate']:.1f}%")
                with col2:
                    st.metric("総損益", f"${stats['net_profit']:.2f}")
                with col3:
                    st.metric("PF", f"{stats['profit_factor']:.2f}")
                with col4:
                    st.metric("総トレード", stats['total'])
                
                st.markdown(generate_harsh_feedback(stats))
                
                st.markdown("")
                st.markdown("")
                
                with st.expander("ℹ️ プロフィットファクター（PF）とは", expanded=False):
                    st.markdown("""
    **プロフィットファクター（PF）の見方**
    
    総利益 ÷ 総損失 で計算される指標
    
    - **1.0未満**: トータルで負けている
    - **1.0〜1.5**: ギリギリ勝っている
    - **1.5〜2.0**: 良好
    - **2.0以上**: 優秀
    - **3.0以上**: プロレベル
    
    **例：**
    総利益 $300、総損失 $150
    PF = 300 ÷ 150 = 2.0（良好）
    """)
                
                    st.markdown(generate_advice(stats))
        else:
            st.info("統計分析にはトレードデータが必要です")
    
    st.markdown("---")
    st.caption(f"⏰ 最終更新: {now_jst.strftime('%Y年%m月%d日 %H:%M:%S')} JST")

except Exception as e:
    st.error(f"❌ エラーが発生しました: {e}")
    import traceback
    error_details = traceback.format_exc()
    st.code(error_details)
    
    # デバッグ情報を表示
    st.warning(f"選択された設定: 時間足={selected_timeframe}, スタイル={trade_style}")
    st.info("この組み合わせでエラーが発生しています。設定を変更してください。")

st.sidebar.markdown("---")
st.sidebar.info(f"""
**設定:**
時間足: {selected_timeframe}
スタイル: {trade_style}
ルール: {len(st.session_state.trade_rules)}件
記録: {len(st.session_state.trade_history)}件
""")

if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
