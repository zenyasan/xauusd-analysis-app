import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import hashlib

st.set_page_config(page_title="XAUUSD分析", page_icon="💰", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    /* 全体背景 - ダークグラデーション */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1d3a 25%, #0f1829 50%, #1e2139 75%, #0a0e27 100%);
        background-attachment: fixed;
    }
    
    /* メインコンテナ */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* タイトル - ネオングラデーション */
    h1 {
        font-family: 'Orbitron', monospace !important;
        background: linear-gradient(90deg, #00d9ff 0%, #7b2ff7 50%, #f107d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900 !important;
        font-size: 2.8rem !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 0 30px rgba(0, 217, 255, 0.5);
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 5px #00d9ff); }
        to { filter: drop-shadow(0 0 20px #7b2ff7); }
    }
    
    /* サブタイトル */
    .stApp p, .stMarkdown p {
        font-family: 'Rajdhani', sans-serif !important;
        color: #8b9dc3 !important;
        text-align: center;
    }
    
    /* メトリックカード - ネオングラデーション */
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', monospace !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #00d9ff 0%, #00b8ff 100%);
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
    
    /* メトリックコンテナ - ネオングラスモーフィズム */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(123, 47, 247, 0.1) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem !important;
        border: 1px solid rgba(0, 217, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 217, 255, 0.2), inset 0 0 20px rgba(0, 217, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: rgba(0, 217, 255, 0.8);
        box-shadow: 0 8px 32px rgba(0, 217, 255, 0.4), inset 0 0 30px rgba(0, 217, 255, 0.2);
        transform: translateY(-5px);
    }
    
    /* タブ - ネオンスタイル */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(10, 14, 39, 0.6);
        border-radius: 15px;
        padding: 10px;
        border: 1px solid rgba(0, 217, 255, 0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600;
        font-size: 1.1rem;
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(123, 47, 247, 0.1) 100%);
        border-radius: 12px;
        color: #00d9ff !important;
        border: 1px solid rgba(0, 217, 255, 0.3);
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.2) 0%, rgba(123, 47, 247, 0.2) 100%);
        border-color: #00d9ff;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.5);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d9ff 0%, #7b2ff7 100%) !important;
        color: #ffffff !important;
        border-color: #00d9ff !important;
        box-shadow: 0 0 30px rgba(0, 217, 255, 0.6);
    }
    
    /* ボタン - ネオン発光 */
    .stButton > button {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700;
        font-size: 1.1rem;
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.2) 0%, rgba(123, 47, 247, 0.2) 100%);
        color: #00d9ff !important;
        border: 2px solid #00d9ff;
        border-radius: 12px;
        padding: 0.6rem 2rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00d9ff 0%, #7b2ff7 100%);
        color: #ffffff !important;
        border-color: #ffffff;
        box-shadow: 0 0 40px rgba(0, 217, 255, 0.8), 0 0 60px rgba(123, 47, 247, 0.5);
        transform: translateY(-3px) scale(1.05);
    }
    
    /* サイドバー - ダークネオン */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1d3a 100%);
        border-right: 2px solid rgba(0, 217, 255, 0.3);
        box-shadow: 5px 0 30px rgba(0, 217, 255, 0.2);
    }
    
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: 'Rajdhani', sans-serif !important;
        color: #00d9ff !important;
        font-weight: 700 !important;
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
    }
    
    /* 入力フィールド - ネオングロー */
    .stTextInput > div > div > input {
        font-family: 'Rajdhani', sans-serif !important;
        background: rgba(10, 14, 39, 0.8) !important;
        border: 1px solid rgba(0, 217, 255, 0.4) !important;
        border-radius: 10px;
        color: #00d9ff !important;
        padding: 12px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00d9ff !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.5) !important;
    }
    
    /* セレクトボックス - ネオンスタイル */
    .stSelectbox > div > div {
        background: rgba(10, 14, 39, 0.8) !important;
        border: 1px solid rgba(0, 217, 255, 0.4) !important;
        border-radius: 10px;
        color: #00d9ff !important;
    }
    
    /* ラジオボタン - ネオン */
    .stRadio > div {
        background: rgba(10, 14, 39, 0.4);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(0, 217, 255, 0.2);
    }
    
    .stRadio label {
        color: #8b9dc3 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 600;
    }
    
    /* 区切り線 - ネオングラデーション */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #00d9ff 50%, transparent 100%);
        margin: 2rem 0;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
    }
    
    /* エキスパンダー - ネオングラスモーフィズム */
    .streamlit-expanderHeader {
        font-family: 'Rajdhani', sans-serif !important;
        font-weight: 700;
        font-size: 1.2rem;
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(123, 47, 247, 0.1) 100%);
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 12px;
        color: #00d9ff !important;
        backdrop-filter: blur(10px);
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #00d9ff;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.4);
    }
    
    /* インフォボックス - カスタムカラー */
    .stAlert {
        background: linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(123, 47, 247, 0.1) 100%);
        border-left: 4px solid #00d9ff;
        border-radius: 12px;
        backdrop-filter: blur(10px);
        color: #8b9dc3 !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    /* マークダウン見出し - ネオングラデーション */
    .stMarkdown h2 {
        font-family: 'Orbitron', monospace !important;
        background: linear-gradient(90deg, #00d9ff 0%, #7b2ff7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        margin-top: 2rem;
    }
    
    .stMarkdown h3 {
        font-family: 'Rajdhani', sans-serif !important;
        color: #00d9ff !important;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.3);
    }
    
    .stMarkdown h4 {
        font-family: 'Rajdhani', sans-serif !important;
        color: #8b9dc3 !important;
        font-weight: 600;
    }
    
    /* リスト - ネオンポイント */
    .stMarkdown ul {
        font-family: 'Rajdhani', sans-serif !important;
        color: #8b9dc3 !important;
    }
    
    .stMarkdown li::marker {
        color: #00d9ff !important;
    }
    
    /* キャプション - ネオングロー */
    .stCaption {
        font-family: 'Rajdhani', sans-serif !important;
        color: #00d9ff !important;
        text-shadow: 0 0 5px rgba(0, 217, 255, 0.3);
    }
    
    /* スピナー - ネオンアニメーション */
    .stSpinner > div {
        border-top-color: #00d9ff !important;
        border-right-color: #7b2ff7 !important;
    }
    
    /* 強調テキスト */
    strong {
        color: #00d9ff !important;
        font-weight: 700;
        text-shadow: 0 0 5px rgba(0, 217, 255, 0.3);
    }
    
    /* スクロールバー - ネオンスタイル */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(10, 14, 39, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00d9ff 0%, #7b2ff7 100%);
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.8);
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

if "trade_rules" not in st.session_state:
    st.session_state.trade_rules = []

st.title("💰 XAUUSD リアルタイム分析アシスタント")
st.markdown("*マルチタイムフレーム対応版*")
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
st.sidebar.header("📝 マイトレードルール")

new_rule = st.sidebar.text_input("新しいルールを追加", placeholder="例: 損失が2%に達したら取引停止")
if st.sidebar.button("➕ ルール追加"):
    if new_rule and new_rule not in st.session_state.trade_rules:
        st.session_state.trade_rules.append(new_rule)
        st.sidebar.success("✅ ルールを追加しました")

if st.session_state.trade_rules:
    st.sidebar.markdown("### 現在のルール:")
    for idx, rule in enumerate(st.session_state.trade_rules):
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            st.sidebar.write(f"✓ {rule}")
        with col2:
            if st.sidebar.button("🗑️", key=f"del_{idx}"):
                st.session_state.trade_rules.pop(idx)
                st.rerun()

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
def calculate_technicals(data):
    df = data.copy()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def find_support_resistance(data):
    recent = data.tail(100)
    resistance = recent['High'].rolling(20).max().iloc[-1]
    support = recent['Low'].rolling(20).min().iloc[-1]
    return support, resistance

def generate_style_analysis(style, current, change_pct, rsi, support, resistance, timeframe):
    long_entry = support + (resistance - support) * 0.2
    long_tp = resistance
    long_sl = support - 20
    
    short_entry = resistance - (resistance - support) * 0.2
    short_tp = support
    short_sl = resistance + 20
    
    if style == "スキャルピング":
        return f"""
## 💨 スキャルピング分析（{timeframe}）

### 推奨エントリー
**即座の動きを狙う超短期売買**

- **現在価格**: ${current:,.2f} ({change_pct:+.2f}%)
- **RSI**: {rsi:.1f}

### エントリーポイント
{"🟢 **ロング検討**" if change_pct > 0 and rsi < 60 else "🔴 **ショート検討**" if change_pct < 0 and rsi > 40 else "⏸️ **様子見**"}

### 具体的戦略

#### 🟢 ロングの場合
- **エントリー**: ${long_entry:,.2f}
- **利確**: ${long_tp:,.2f}
- **損切り**: ${long_sl:,.2f}
- **リスクリワード**: 1:{(long_tp - long_entry)/(long_entry - long_sl):.2f}

#### 🔴 ショートの場合
- **エントリー**: ${short_entry:,.2f}
- **利確**: ${short_tp:,.2f}
- **損切り**: ${short_sl:,.2f}
- **リスクリワード**: 1:{(short_entry - short_tp)/(short_sl - short_entry):.2f}

### 注意点
- 経済指標発表30分前は避ける
- スプレッドが広がる時間は見送り
- 連続3回負けたら休憩
"""
    elif style == "デイトレード":
        return f"""
## 📊 デイトレード分析（{timeframe}）

### 本日のトレード戦略

- **現在価格**: ${current:,.2f} ({change_pct:+.2f}%)
- **RSI**: {rsi:.1f}

### トレンド判定
{"📈 **上昇トレンド** - ロング優勢" if change_pct > 0.3 else "📉 **下落トレンド** - ショート優勢" if change_pct < -0.3 else "➡️ **レンジ** - 逆張り戦略"}

### 具体的戦略

#### 🟢 ロングの場合
- **エントリー**: ${long_entry:,.2f}
- **利確目標1**: ${(long_entry + long_tp) / 2:,.2f}（50%決済）
- **利確目標2**: ${long_tp:,.2f}（残り50%）
- **損切り**: ${long_sl:,.2f}

#### 🔴 ショートの場合  
- **エントリー**: ${short_entry:,.2f}
- **利確目標1**: ${(short_entry + short_tp) / 2:,.2f}（50%決済）
- **利確目標2**: ${short_tp:,.2f}（残り50%）
- **損切り**: ${short_sl:,.2f}

### 注意点
- {"RSI買われすぎ、反落注意" if rsi > 70 else "RSI売られすぎ、反発期待" if rsi < 30 else "RSI中立、トレンドに従う"}
- ポジションは必ず当日中に決済
"""
    else:
        return f"""
## 📈 スイングトレード分析（{timeframe}）

### 中期トレンド分析

- **現在価格**: ${current:,.2f} ({change_pct:+.2f}%)
- **RSI**: {rsi:.1f}

### 大局的トレンド
{"🟢 **強気相場**" if change_pct > 1.0 else "🔴 **弱気相場**" if change_pct < -1.0 else "🟡 **中立**"}

### 具体的戦略

#### 🟢 ロングの場合
- **エントリーゾーン**: ${support:,.0f}〜${long_entry:,.0f}
- **第1目標**: ${long_entry + 50:,.0f}（30%利確）
- **第2目標**: ${long_tp:,.0f}（40%利確）  
- **第3目標**: ${long_tp + 100:,.0f}（残り30%）
- **損切り**: ${long_sl:,.0f}

#### 🔴 ショートの場合
- **エントリーゾーン**: ${short_entry:,.0f}〜${resistance:,.0f}
- **第1目標**: ${short_entry - 50:,.0f}（30%利確）
- **第2目標**: ${short_tp:,.0f}（40%利確）
- **第3目標**: ${short_tp - 100:,.0f}（残り30%）
- **損切り**: ${short_sl:,.0f}

### 注意点
- 地政学リスクに注意
- FRB発言・経済指標に敏感
"""

def display_trade_rules():
    if st.session_state.trade_rules:
        st.markdown("### 📋 あなたのトレードルール")
        for idx, rule in enumerate(st.session_state.trade_rules, 1):
            st.markdown(f"**{idx}.** {rule}")
    else:
        st.info("💡 左サイドバーから自分のトレードルールを追加できます")

try:
    with st.spinner(f'📊 {selected_timeframe}データを取得中...'):
        data = get_gold_data(period, interval)
        if data is None or len(data) == 0:
            st.error("❌ データ取得失敗")
            st.stop()
        df = calculate_technicals(data)
    
    current = data['Close'].iloc[-1]
    previous = data['Close'].iloc[-2]
    change = current - previous
    pct = (change / previous) * 100
    rsi = df['RSI'].iloc[-1]
    support, resistance = find_support_resistance(df)
    
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
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='XAUUSD', increasing_line_color='#00d9ff', decreasing_line_color='#f107d4'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA20', line=dict(color='#00d9ff', width=2)))
    if len(df) >= 50:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA50', line=dict(color='#7b2ff7', width=2)))
    fig.add_hline(y=support, line_dash="dash", line_color="#00ff88", annotation_text="サポート", line_width=2)
    fig.add_hline(y=resistance, line_dash="dash", line_color="#ff0088", annotation_text="レジスタンス", line_width=2)
    fig.add_hline(y=5000, line_dash="dot", line_color="#ffff00", annotation_text="5,000", line_width=2)
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
    
    tabs = st.tabs(["📊 選択中", "💨 スキャル", "📈 デイトレ", "📉 スイング"])
    
    with tabs[0]:
        st.markdown(generate_style_analysis(trade_style, current, pct, rsi, support, resistance, selected_timeframe))
        st.markdown("---")
        display_trade_rules()
    
    with tabs[1]:
        st.markdown(generate_style_analysis("スキャルピング", current, pct, rsi, support, resistance, selected_timeframe))
        st.markdown("---")
        display_trade_rules()
    
    with tabs[2]:
        st.markdown(generate_style_analysis("デイトレード", current, pct, rsi, support, resistance, selected_timeframe))
        st.markdown("---")
        display_trade_rules()
    
    with tabs[3]:
        st.markdown(generate_style_analysis("スイングトレード", current, pct, rsi, support, resistance, selected_timeframe))
        st.markdown("---")
        display_trade_rules()
    
    st.markdown("---")
    st.caption(f"⏰ 最終更新: {datetime.now().strftime('%H:%M:%S')}")
    if st.button("🔄 更新"):
        st.cache_data.clear()
        st.rerun()

except Exception as e:
    st.error(f"❌ エラー: {e}")

st.sidebar.markdown("---")
st.sidebar.info(f"""
**現在の設定:**
- 時間足: {selected_timeframe}
- スタイル: {trade_style}
- マイルール: {len(st.session_state.trade_rules)}件
""")
