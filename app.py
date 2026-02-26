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

st.set_page_config(page_title="XAUUSD分析", page_icon="💰", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1d3a 25%, #0f1829 50%, #1e2139 75%, #0a0e27 100%);
        background-attachment: fixed;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    h1 {
        font-family: 'Orbitron', monospace !important;
        background: linear-gradient(90deg, #00aaff 0%, #0055ff 50%, #aa00ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900 !important;
        font-size: 2.8rem !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 0 30px rgba(0, 170, 255, 0.5);
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 5px #00aaff); }
        to { filter: drop-shadow(0 0 20px #0055ff); }
    }
    
    .stApp p, .stMarkdown p {
        font-family: 'Rajdhani', sans-serif !important;
        color: #8b9dc3 !important;
        text-align: center;
    }
    
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', monospace !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #00aaff 0%, #0055ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.1rem !important;
        color: #8b9dc3 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1rem !important;
    }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(0, 170, 255, 0.1) 0%, rgba(0, 85, 255, 0.1) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem !important;
        border: 1px solid rgba(0, 170, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 170, 255, 0.2), inset 0 0 20px rgba(0, 170, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: rgba(0, 170, 255, 0.8);
        box-shadow: 0 8px 32px rgba(0, 170, 255, 0.4), inset 0 0 30px rgba(0, 170, 255, 0.2);
        transform: translateY(-5px);
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
        font-size: 1.1rem;
        background: linear-gradient(135deg, rgba(0, 170, 255, 0.2) 0%, rgba(0, 85, 255, 0.2) 100%);
        color: #00aaff !important;
        border: 2px solid #00aaff;
        border-radius: 12px;
        padding: 0.6rem 2rem;
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
    .stTextArea > div > div > textarea {
        font-family: 'Rajdhani', sans-serif !important;
        background: rgba(10, 14, 39, 0.8) !important;
        border: 1px solid rgba(0, 170, 255, 0.4) !important;
        border-radius: 10px;
        color: #00aaff !important;
        padding: 12px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
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

def save_trades_to_file(trades, username="default"):
    os.makedirs("user_data", exist_ok=True)
    with open(f"user_data/{username}_trades.json", "w", encoding="utf-8") as f:
        json.dump(trades, f, ensure_ascii=False, indent=2)

def load_trades_from_file(username="default"):
    try:
        with open(f"user_data/{username}_trades.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

if "trade_rules" not in st.session_state:
    st.session_state.trade_rules = load_rules_from_file()

if "trade_history" not in st.session_state:
    st.session_state.trade_history = load_trades_from_file()

st.title("💰 XAUUSD リアルタイム分析アシスタント")
st.markdown("*マルチタイムフレーム対応版 - 高精度戦略*")
st.markdown("---")

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
        return data
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return None

@st.cache_data(ttl=60)
def calculate_advanced_technicals(data):
    df = data.copy()
    
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']
    
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df['ATR'] = true_range.rolling(14).mean()
    
    df['Pivot'] = (df['High'].shift(1) + df['Low'].shift(1) + df['Close'].shift(1)) / 3
    df['R1'] = 2 * df['Pivot'] - df['Low'].shift(1)
    df['S1'] = 2 * df['Pivot'] - df['High'].shift(1)
    df['R2'] = df['Pivot'] + (df['High'].shift(1) - df['Low'].shift(1))
    df['S2'] = df['Pivot'] - (df['High'].shift(1) - df['Low'].shift(1))
    
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
    
    rr_long = (targets['long']['tp2'] - targets['long']['entry']) / (targets['long']['entry'] - targets['long']['sl'])
    rr_short = (targets['short']['entry'] - targets['short']['tp2']) / (targets['short']['sl'] - targets['short']['entry'])
    
    if style == "スキャルピング":
        return f"""
## 💨 スキャルピング分析（{timeframe}）

### 📊 テクニカル状況
- **現在価格**: ${current:,.2f} ({change_pct:+.2f}%)
- **RSI**: {rsi:.1f} {"⚠️ 買われすぎ" if rsi > 70 else "✅ 売られすぎ" if rsi < 30 else "➡️ 中立"}
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
- **RSI**: {rsi:.1f}
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
- **RSI**: {rsi:.1f}
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

def display_trade_rules():
    if st.session_state.trade_rules:
        st.markdown("### 📋 あなたのトレードルール")
        for idx, rule in enumerate(st.session_state.trade_rules, 1):
            st.markdown(f"**{idx}.** {rule}")
    else:
        st.info("💡 左サイドバーから自分のトレードルールを追加できます")

def analyze_trade_simple(trade_data):
    trade_type = trade_data['type']
    entry = trade_data['entry_price']
    exit = trade_data['exit_price']
    pnl = (exit - entry) if trade_type == "ロング" else (entry - exit)
    pnl_pct = (pnl / entry) * 100
    
    analysis = f"""
## 📊 トレード分析結果

### 基本情報
- **タイプ**: {trade_type}
- **エントリー**: ${entry:,.2f}
- **決済**: ${exit:,.2f}
- **損益**: ${pnl:,.2f} ({pnl_pct:+.2f}%)

### ✅ 良かった点
"""
    
    if pnl > 0:
        analysis += f"""
- ✅ 利益を確保できた（+${pnl:.2f}）
- ✅ 方向性の判断が正しかった
"""
        if trade_data['entry_reason']:
            analysis += f"- ✅ エントリー理由が明確: {trade_data['entry_reason']}\n"
    else:
        analysis += "- （利益が出なかったため該当なし）\n"
    
    analysis += "\n### 🔧 改善すべき点\n"
    
    if pnl < 0:
        analysis += f"""
- ⚠️ 損失が発生（-${abs(pnl):.2f}）
- ⚠️ エントリータイミングまたは方向性の再検討が必要
- ⚠️ 損切りルールの見直し
"""
    
    if not trade_data['entry_reason']:
        analysis += "- ⚠️ エントリー理由が不明確 - 次回は必ず記録する\n"
    
    if not trade_data['exit_reason']:
        analysis += "- ⚠️ 決済理由が不明確 - 計画的な決済を\n"
    
    analysis += "\n### 📌 次回注意すべきポイント\n"
    analysis += f"""
- 📍 同じ{trade_type}でエントリーする場合、エントリー価格の±10ドル圏内でのみ検討
- 📍 損切りは必ずエントリー時に設定する
- 📍 利確目標を2段階に分ける（50%ずつ）
- 📍 感情的な判断を避け、ルールに従う
"""
    
    if trade_data['emotion'] in ['焦り', '不安', '興奮']:
        analysis += f"\n⚠️ **感情状態が「{trade_data['emotion']}」でした。冷静な判断ができていない可能性があります。**\n"
    
    analysis += """

### 🧠 推奨される思考プロセス

1. **エントリー前**
   - テクニカル指標を3つ以上確認
   - リスクリワード比率が1:2以上か確認
   - 損切り価格を決定してから注文

2. **ポジション保有中**
   - 一度設定した損切りは動かさない
   - 利確目標に達したら機械的に決済
   - ニュースをチェックするが、過剰反応しない

3. **決済後**
   - すぐに次のトレードをしない
   - 記録を残す（このような分析のため）
   - 1時間は休憩する

### 💡 このトレードから学べる教訓
"""
    
    if pnl > 0:
        analysis += f"- 成功パターンを記録し、再現性を高める\n- ただし、過信は禁物\n"
    else:
        analysis += f"- 失敗から学ぶことが最も重要\n- 同じミスを繰り返さないためにルール化する\n"
    
    return analysis

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
        st.success("✅ リアルタイム価格取得成功")
    else:
        current = data['Close'].iloc[-1]
        previous = data['Close'].iloc[-2]
        st.warning("⚠️ リアルタイム価格取得失敗、最新の履歴価格を使用")
    
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
    
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.metric("💰 現在価格", f"${current:,.2f}", f"{change:+.2f} ({pct:+.2f}%)")
    with row1_col2:
        rsi_status = "買われすぎ" if rsi > 70 else "売られすぎ" if rsi < 30 else "中立"
        st.metric("📈 RSI (14)", f"{rsi:.1f}", rsi_status)
    
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.metric("🔽 サポート", f"${support:,.0f}")
    with row2_col2:
        st.metric("🔼 レジスタンス", f"${resistance:,.0f}")
    
    st.markdown("---")
    
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
    
    fig.add_hline(y=support, line_dash="dash", line_color="#00ff88", annotation_text="サポート", line_width=2)
    fig.add_hline(y=resistance, line_dash="dash", line_color="#ff0088", annotation_text="レジスタンス", line_width=2)
    fig.add_hline(y=pivot, line_dash="dot", line_color="#ffaa00", annotation_text="ピボット", line_width=2)
    
    fig.update_layout(
        title=f'📈 XAUUSD {selected_timeframe}チャート',
        height=600,
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        paper_bgcolor='rgba(10,14,39,0.8)',
        plot_bgcolor='rgba(10,14,39,0.5)',
        font=dict(family='Rajdhani', color='#8b9dc3')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    analysis_options = {
        "選択中のスタイル": trade_style,
        "スキャルピング": "スキャルピング",
        "デイトレード": "デイトレード",
        "スイングトレード": "スイングトレード"
    }
    
    selected_analysis = st.selectbox(
        "📊 分析タイプを選択",
        list(analysis_options.keys()),
        index=0
    )
    
    display_style = analysis_options[selected_analysis]
    
    st.markdown(generate_advanced_analysis(
        display_style, current, pct, rsi, macd, macd_signal, 
        atr, support, resistance, pivot, r1, s1, selected_timeframe
    ))
    
    st.markdown("---")
    display_trade_rules()
    
    st.markdown("---")
    st.header("📝 トレード記録分析")
    
    with st.expander("新しいトレードを記録して分析", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            trade_date = st.date_input("日時")
            trade_type = st.selectbox("タイプ", ["ロング", "ショート"])
            entry_price = st.number_input("エントリー価格", value=float(current), format="%.2f")
            exit_price = st.number_input("決済価格", value=float(current + 50 if trade_type == "ロング" else current - 50), format="%.2f")
        
        with col2:
            lot_size = st.number_input("ロット数", value=0.01, format="%.2f")
            entry_reason = st.text_area("エントリー理由", placeholder="例: RSI30で反発、MACDゴールデンクロス")
            exit_reason = st.text_area("決済理由", placeholder="例: 利確目標到達、損切り")
            emotion = st.selectbox("その時の感情", ["冷静", "焦り", "自信", "不安", "興奮"])
        
        if st.button("🔍 分析を実行"):
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
            
            analysis = analyze_trade_simple(trade_data)
            st.markdown(analysis)
            st.success("✅ トレード記録を保存しました")
    
    if st.session_state.trade_history:
        with st.expander(f"📚 過去のトレード記録（{len(st.session_state.trade_history)}件）"):
            for idx, trade in enumerate(reversed(st.session_state.trade_history[-10:])):
                pnl = (trade['exit_price'] - trade['entry_price']) if trade['type'] == "ロング" else (trade['entry_price'] - trade['exit_price'])
                st.markdown(f"**{trade['date']}** - {trade['type']} - 損益: ${pnl:.2f}")
    
    st.markdown("---")
    jst = pytz.timezone('Asia/Tokyo')
    now_jst = datetime.now(jst)
    st.caption(f"⏰ 最終更新: {now_jst.strftime('%Y年%m月%d日 %H:%M:%S')} JST")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 今すぐ更新", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col_btn2:
        if auto_refresh:
            st.info(f"⏰ {refresh_interval}秒後に自動更新")

except Exception as e:
    st.error(f"❌ エラー: {e}")
    import traceback
    st.code(traceback.format_exc())

st.sidebar.markdown("---")
st.sidebar.info(f"""
**現在の設定:**
- 時間足: {selected_timeframe}
- スタイル: {trade_style}
- マイルール: {len(st.session_state.trade_rules)}件
- トレード記録: {len(st.session_state.trade_history)}件
""")

if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
