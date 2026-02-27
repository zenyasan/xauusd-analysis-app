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

st.set_page_config(page_title="XAUUSD分析", page_icon="💰", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1d3a 25%, #0f1829 50%, #1e2139 75%, #0a0e27 100%);
        background-attachment: fixed;
    }
    
    .main .block-container {
        padding-top: 18rem;
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
        padding: 1.5rem 2rem 1rem 2rem;
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
        font-size: 1.8rem;
        text-align: center;
        margin: 0;
        padding: 0;
        line-height: 1.3;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    .sticky-subtitle {
        font-family: 'Rajdhani', sans-serif;
        color: #8b9dc3;
        text-align: center;
        font-size: 0.9rem;
        margin: 0.3rem 0 0.8rem 0;
    }
    
    @media (max-width: 768px) {
        .sticky-header {
            top: 3rem;
        }
        .sticky-title {
            font-size: 1.3rem;
        }
        .sticky-subtitle {
            font-size: 0.8rem;
        }
        .main .block-container {
            padding-top: 20rem;
        }
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 5px #00aaff); }
        to { filter: drop-shadow(0 0 20px #0055ff); }
    }
    
    .stApp p, .stMarkdown p {
        font-family: 'Rajdhani', sans-serif !important;
        color: #8b9dc3 !important;
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
</style>
""", unsafe_allow_html=True)

def check_password():
    def password_entered():
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == "4e42de48f9cdf95d8cbf5ad17f11a63601120eb1cdaa35eae088bb75196e4a67":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.markdown("# 🔒 XAUUSD分析アプリ")
        st.text_input("パスワード", type="password", on_change=password_entered, key="password")
        st.info("💡 パスワードを入力してください")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("# 🔒 XAUUSD分析アプリ")
        st.text_input("パスワード", type="password", on_change=password_entered, key="password")
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

def extract_numbers_from_image(image):
    """画像から数値を抽出する簡易OCR（Pytesseract不使用版）"""
    try:
        import easyocr
        reader = easyocr.Reader(['en', 'ja'])
        result = reader.readtext(image)
        
        extracted_text = " ".join([text[1] for text in result])
        
        numbers = re.findall(r'\d+\.?\d*', extracted_text)
        prices = [float(num) for num in numbers if float(num) > 1000 and float(num) < 10000]
        lots = [float(num) for num in numbers if float(num) > 0 and float(num) < 100]
        
        trade_type = "ロング"
        if any(word in extracted_text.upper() for word in ['SELL', 'SHORT', 'ショート', '売']):
            trade_type = "ショート"
        elif any(word in extracted_text.upper() for word in ['BUY', 'LONG', 'ロング', '買']):
            trade_type = "ロング"
        
        return {
            'type': trade_type,
            'prices': prices[:5] if len(prices) > 0 else [5000.0, 5050.0],
            'lots': lots[:3] if len(lots) > 0 else [0.01],
            'raw_text': extracted_text
        }
    except ImportError:
        return simple_number_extraction(image)
    except Exception as e:
        st.error(f"OCRエラー: {e}")
        return simple_number_extraction(image)

def simple_number_extraction(image):
    """OCRライブラリなしのフォールバック"""
    return {
        'type': 'ロング',
        'prices': [5000.0, 5050.0],
        'lots': [0.01],
        'raw_text': 'OCRライブラリが利用できません。手動で入力してください。'
    }

def calculate_trade_statistics(trades):
    if not trades:
        return None
    
    total = len(trades)
    wins = 0
    losses = 0
    total_profit = 0
    total_loss = 0
    
    long_wins = 0
    long_total = 0
    short_wins = 0
    short_total = 0
    
    emotion_stats = defaultdict(lambda: {'wins': 0, 'total': 0})
    
    for trade in trades:
        pnl = (trade['exit_price'] - trade['entry_price']) if trade['type'] == "ロング" else (trade['entry_price'] - trade['exit_price'])
        
        if pnl > 0:
            wins += 1
            total_profit += pnl
        else:
            losses += 1
            total_loss += abs(pnl)
        
        if trade['type'] == "ロング":
            long_total += 1
            if pnl > 0:
                long_wins += 1
        else:
            short_total += 1
            if pnl > 0:
                short_wins += 1
        
        emotion_stats[trade['emotion']]['total'] += 1
        if pnl > 0:
            emotion_stats[trade['emotion']]['wins'] += 1
    
    win_rate = (wins / total * 100) if total > 0 else 0
    avg_profit = (total_profit / wins) if wins > 0 else 0
    avg_loss = (total_loss / losses) if losses > 0 else 0
    profit_factor = (total_profit / total_loss) if total_loss > 0 else 0
    net_profit = total_profit - total_loss
    
    long_wr = (long_wins / long_total * 100) if long_total > 0 else 0
    short_wr = (short_wins / short_total * 100) if short_total > 0 else 0
    
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
        'long_wr': long_wr,
        'short_wr': short_wr,
        'long_total': long_total,
        'short_total': short_total,
        'emotion_stats': dict(emotion_stats)
    }

def generate_harsh_feedback(stats):
    if not stats:
        return "データ不足。最低10トレードは記録してください。"
    
    feedback = "## 🔴 あなたの弱点\n\n"
    
    if stats['win_rate'] < 40:
        feedback += "- **勝率が40%未満。完全に失敗しています。** エントリータイミングが全く機能していない。根本的に見直しが必要です。\n"
    elif stats['win_rate'] < 50:
        feedback += "- **勝率50%未満。負け越しています。** トレード手法が間違っている可能性が高い。このまま続けると資金を失います。\n"
    
    if stats['avg_loss'] > stats['avg_profit']:
        feedback += "- **損大利小になっています。** 損切りが遅すぎる、または利確が早すぎる。トレーダーとして致命的な欠陥です。\n"
    
    if stats['profit_factor'] < 1:
        feedback += "- **プロフィットファクター1未満。トータルで負けています。** このままでは破産確定です。今すぐトレードを止めて見直してください。\n"
    elif stats['profit_factor'] < 1.5:
        feedback += "- **プロフィットファクターが低すぎます。** ギリギリ勝っているだけ。安定して勝てていません。\n"
    
    if stats['long_total'] > 0 and stats['short_total'] == 0:
        feedback += "- **ロングしかトレードしていない。** 完全にバイアスがかかっています。相場は上下するもの。片方しか取れないのは未熟です。\n"
    elif stats['short_total'] > 0 and stats['long_total'] == 0:
        feedback += "- **ショートしかトレードしていない。** 完全にバイアスがかかっています。機会損失が大きすぎます。\n"
    
    emotion_issues = []
    for emotion, data in stats['emotion_stats'].items():
        if emotion in ['焦り', '不安', '興奮'] and data['total'] > 0:
            wr = (data['wins'] / data['total'] * 100) if data['total'] > 0 else 0
            if wr < 50:
                emotion_issues.append(f"{emotion}（勝率{wr:.0f}%）")
    
    if emotion_issues:
        feedback += f"- **感情的なトレードで負けています: {', '.join(emotion_issues)}。** メンタルコントロールができていない。冷静さを完全に欠いています。\n"
    
    if stats['total'] < 10:
        feedback += "- **トレード数が少なすぎます。** サンプル数が足りず、統計的に意味がありません。もっと経験を積んでください。\n"
    
    return feedback

def generate_advice(stats):
    if not stats:
        return ""
    
    advice = "## 💡 改善のためのアドバイス\n\n"
    
    if stats['win_rate'] > 50 and stats['avg_profit'] < stats['avg_loss'] * 1.5:
        advice += "- 勝率は悪くないですが、利益が小さい。**利確を伸ばす練習をしてください。** トレンドに乗り続けることを意識しましょう。\n"
    
    if stats['win_rate'] < 50 and stats['profit_factor'] > 1:
        advice += "- 勝率は低いですが利益は出ています。**方向性は間違っていません。** エントリー精度を上げることに集中してください。\n"
    
    if stats['long_total'] > 0 and stats['short_total'] > 0:
        if abs(stats['long_wr'] - stats['short_wr']) > 20:
            better = "ロング" if stats['long_wr'] > stats['short_wr'] else "ショート"
            worse = "ショート" if better == "ロング" else "ロング"
            advice += f"- **{better}の勝率が高い（{max(stats['long_wr'], stats['short_wr']):.0f}%）。** {worse}は控えめにして、{better}に集中する戦略も有効です。\n"
    
    if stats['profit_factor'] > 2:
        advice += "- プロフィットファクターが優秀です。**現在の手法を維持してください。** 無理に変える必要はありません。\n"
    
    for emotion, data in stats['emotion_stats'].items():
        if emotion == '冷静' and data['total'] > 0:
            wr = (data['wins'] / data['total'] * 100) if data['total'] > 0 else 0
            if wr > 60:
                advice += f"- **「冷静」な時の勝率が{wr:.0f}%と高い。** 感情的にならないことが成功の鍵です。このマインドを維持してください。\n"
    
    advice += "\n### 🎯 推奨アクション\n"
    advice += "- エントリー前に必ず損切り価格を決める\n"
    advice += "- 利確は2段階に分ける（50%ずつ）\n"
    advice += "- 連続3回負けたら必ず休憩する\n"
    advice += "- トレード記録を毎回つける\n"
    
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
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; margin-top: 0.5rem;">
        <div style="background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 85, 255, 0.1) 100%); border: 1px solid rgba(0, 170, 255, 0.3); border-radius: 10px; padding: 0.5rem; text-align: center;">
            <div style="font-size: 0.7rem; color: #8b9dc3;">🔽 サポート</div>
            <div style="font-size: 1rem; font-weight: bold; background: linear-gradient(135deg, #00aaff 0%, #0055ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${st.session_state.support_value:,.0f}</div>
        </div>
        <div style="background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 85, 255, 0.1) 100%); border: 1px solid rgba(0, 170, 255, 0.3); border-radius: 10px; padding: 0.5rem; text-align: center;">
            <div style="font-size: 0.7rem; color: #8b9dc3;">💰 現在価格</div>
            <div style="font-size: 1rem; font-weight: bold; background: linear-gradient(135deg, #00aaff 0%, #0055ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${st.session_state.current_price:,.2f}</div>
            <div style="font-size: 0.7rem; color: #8b9dc3;">{st.session_state.price_change:+.2f} ({st.session_state.price_pct:+.2f}%)</div>
        </div>
        <div style="background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 85, 255, 0.1) 100%); border: 1px solid rgba(0, 170, 255, 0.3); border-radius: 10px; padding: 0.5rem; text-align: center;">
            <div style="font-size: 0.7rem; color: #8b9dc3;">🔼 レジスタンス</div>
            <div style="font-size: 1rem; font-weight: bold; background: linear-gradient(135deg, #00aaff 0%, #0055ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${st.session_state.resistance_value:,.0f}</div>
        </div>
        <div style="background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 85, 255, 0.1) 100%); border: 1px solid rgba(0, 170, 255, 0.3); border-radius: 10px; padding: 0.5rem; text-align: center;">
            <div style="font-size: 0.7rem; color: #8b9dc3;">📈 RSI (7)</div>
            <div style="font-size: 1rem; font-weight: bold; background: linear-gradient(135deg, #00aaff 0%, #0055ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{st.session_state.rsi_value:.1f}</div>
            <div style="font-size: 0.7rem; color: #8b9dc3;">{st.session_state.rsi_status}</div>
        </div>
    </div>
</div>
''', unsafe_allow_html=True)

st.sidebar.header("⚙️ 設定")

timeframe_options = {
    "1分足": ("1m", "1d"),
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
auto_refresh = st.sidebar.checkbox("自動更新を有効化", value=False)
if auto_refresh:
    refresh_interval = st.sidebar.slider("更新間隔（秒）", 30, 300, 60)

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
        response = requests.get("https://api.metals.live/v1/spot/gold", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return float(data[0]['price'])
    except:
        pass
    
    try:
        ticker = yf.Ticker("GC=F")
        latest = ticker.history(period="1d", interval="1m")
        if len(latest) > 0:
            return latest['Close'].iloc[-1]
    except:
        pass
    
    return None

@st.cache_data(ttl=60)
def get_gold_data(period, interval):
    try:
        ticker = yf.Ticker("GC=F")
        data = ticker.history(period=period, interval=interval)
        if len(data) > 0 and data.index.tz is not None:
            data.index = data.index.tz_convert('Asia/Tokyo')
        return data
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return None

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
        return f"""
## 💨 スキャルピング分析（{timeframe}）

### 📊 テクニカル状況
- **現在価格**: ${current:,.2f} ({change_pct:+.2f}%)
- **RSI (7)**: {rsi:.1f} {"⚠️ 買われすぎ" if rsi > 70 else "✅ 売られすぎ" if rsi < 30 else "➡️ 中立"}
- **MACD**: {macd_trend}
- **ATR**: {atr:.2f}（ボラティリティ指標）
- **ピボット**: ${pivot:,.2f}

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
- スプレッド考慮：エントリーは±3ドルの余裕を持つ
- 経済指標30分前は避ける
- 連続3回負けたら1時間休憩必須
- ATRが平均の1.5倍以上の時は見送り
"""
    
    elif style == "デイトレード":
        return f"""
## 📊 デイトレード分析（{timeframe}）

### 📈 市場環境分析
- **現在価格**: ${current:,.2f} ({change_pct:+.2f}%)
- **RSI (7)**: {rsi:.1f}
- **MACD**: {macd_trend}
- **ATR**: {atr:.2f}
- **ピボットポイント**: ${pivot:,.2f}
- **レジスタンス**: R1=${r1:,.2f}
- **サポート**: S1=${s1:,.2f}

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
    
    else:
        return f"""
## 📈 スイングトレード分析（{timeframe}）

### 🌍 マクロ環境
- **現在価格**: ${current:,.2f} ({change_pct:+.2f}%)
- **週次トレンド**: {"上昇" if change_pct > 1 else "下降" if change_pct < -1 else "中立"}
- **RSI (7)**: {rsi:.1f}
- **MACD**: {macd_trend}
