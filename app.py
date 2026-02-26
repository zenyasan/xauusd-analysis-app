import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import hashlib

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

st.set_page_config(page_title="XAUUSD分析", page_icon="💰", layout="wide")
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
    df['BB_middle'] = df['Close'].rolling(window=20).mean()
    df['BB_std'] = df['Close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (df['BB_std'] * 2)
    df['BB_lower'] = df['BB_middle'] - (df['BB_std'] * 2)
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
- **エントリー**: ${long_entry:,.2f}（サポート反発を狙う）
- **利確**: ${long_tp:,.2f}（+{long_tp - long_entry:.1f}ドル）
- **損切り**: ${long_sl:,.2f}（-{long_entry - long_sl:.1f}ドル）
- **リスクリワード**: 1:{(long_tp - long_entry)/(long_entry - long_sl):.2f}

#### 🔴 ショートの場合
- **エントリー**: ${short_entry:,.2f}（レジスタンス反落を狙う）
- **利確**: ${short_tp:,.2f}（+{short_entry - short_tp:.1f}ドル）
- **損切り**: ${short_sl:,.2f}（-{short_sl - short_entry:.1f}ドル）
- **リスクリワード**: 1:{(short_entry - short_tp)/(short_sl - short_entry):.2f}

### 注意点
- 経済指標発表30分前は避ける
- スプレッドが広がる時間は見送り
- 連続3回負けたら休憩
- 1トレード最大5分以内
"""
    elif style == "デイトレード":
        return f"""
## 📊 デイトレード分析（{timeframe}）

### 本日のトレード戦略
**1日の値動きを活用した売買**

- **現在価格**: ${current:,.2f} ({change_pct:+.2f}%)
- **RSI**: {rsi:.1f}

### トレンド判定
{"📈 **上昇トレンド** - ロング優勢" if change_pct > 0.3 else "📉 **下落トレンド** - ショート優勢" if change_pct < -0.3 else "➡️ **レンジ** - 逆張り戦略"}

### 具体的戦略

#### 🟢 ロングの場合
- **エントリー**: ${long_entry:,.2f}〜${long_entry + 10:,.2f}（押し目買い）
- **利確目標1**: ${(long_entry + long_tp) / 2:,.2f}（50%決済）
- **利確目標2**: ${long_tp:,.2f}（残り50%決済）
- **損切り**: ${long_sl:,.2f}（必須）
- **想定利益**: +{long_tp - long_entry:.1f}ドル
- **許容損失**: -{long_entry - long_sl:.1f}ドル

#### 🔴 ショートの場合  
- **エントリー**: ${short_entry - 10:,.2f}〜${short_entry:,.2f}（戻り売り）
- **利確目標1**: ${(short_entry + short_tp) / 2:,.2f}（50%決済）
- **利確目標2**: ${short_tp:,.2f}（残り50%決済）
- **損切り**: ${short_sl:,.2f}（必須）
- **想定利益**: +{short_entry - short_tp:.1f}ドル
- **許容損失**: -{short_sl - short_entry:.1f}ドル

### 時間帯別戦略
- 🌅 **9:00-12:00 (東京)**: トレンドフォロー
- 🌆 **16:00-19:00 (欧州)**: ボラティリティ高
- 🌙 **22:00-02:00 (NY)**: メインセッション

### 注意点
- {"RSI買われすぎ、反落注意" if rsi > 70 else "RSI売られすぎ、反発期待" if rsi < 30 else "RSI中立、トレンドに従う"}
- ポジションは必ず当日中に決済
"""
    else:
        return f"""
## 📈 スイングトレード分析（{timeframe}）

### 中期トレンド分析
**数日〜数週間保有する戦略**

- **現在価格**: ${current:,.2f} ({change_pct:+.2f}%)
- **RSI**: {rsi:.1f}

### 大局的トレンド
{"🟢 **強気相場** - ロングポジション推奨" if change_pct > 1.0 else "🔴 **弱気相場** - ショートポジション推奨" if change_pct < -1.0 else "🟡 **中立** - 明確なトレンドなし"}

### 具体的戦略

#### 🟢 ロングの場合
- **エントリーゾーン**: ${support:,.0f}〜${long_entry:,.0f}ドル
- **第1目標**: ${long_entry + 50:,.0f}ドル（30%利確）
- **第2目標**: ${long_tp:,.0f}ドル（40%利確）  
- **第3目標**: ${long_tp + 100:,.0f}ドル（残り30%）
- **損切り**: ${long_sl:,.0f}ドル（資金の2%以下）
- **想定保有期間**: 3日〜2週間

#### 🔴 ショートの場合
- **エントリーゾーン**: ${short_entry:,.0f}〜${resistance:,.0f}ドル
- **第1目標**: ${short_entry - 50:,.0f}ドル（30%利確）
- **第2目標**: ${short_tp:,.0f}ドル（40%利確）
- **第3目標**: ${short_tp - 100:,.0f}ドル（残り30%）
- **損切り**: ${short_sl:,.0f}ドル（資金の2%以下）
- **想定保有期間**: 3日〜2週間

### リスク管理
- ポジションサイズ: 資金の2〜5%
- 段階的な利確を推奨
- 週末は必ずポジション確認

### 注意点
- 地政学リスクに注意
- FRB発言・経済指標に敏感
- トレンド転換のサインを見逃さない
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
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='XAUUSD'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA20', line=dict(color='orange', width=2)))
    if len(df) >= 50:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA50', line=dict(color='blue', width=2)))
    fig.add_hline(y=support, line_dash="dash", line_color="green", annotation_text="サポート")
    fig.add_hline(y=resistance, line_dash="dash", line_color="red", annotation_text="レジスタンス")
    fig.add_hline(y=5000, line_dash="dot", line_color="yellow", annotation_text="5,000")
    fig.update_layout(title=f'📈 XAUUSD {selected_timeframe}チャート', height=600, xaxis_rangeslider_visible=False, template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    tabs = st.tabs(["📊 選択中の分析", "💨 スキャルピング", "📈 デイトレード", "📉 スイング"])
    
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
