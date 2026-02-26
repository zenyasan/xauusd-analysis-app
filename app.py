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

selected_timeframe = st.sidebar.selectbox(
    "時間足",
    list(timeframe_options.keys()),
    index=3
)

interval, period = timeframe_options[selected_timeframe]

trade_style = st.sidebar.radio(
    "トレードスタイル",
    ["スキャルピング", "デイトレード", "スイングトレード"],
    index=1
)

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
    df['SMA_200'] = df['Close'].rolling(window=200).mean()
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
    if style == "スキャルピング":
        return f"""
## 💨 スキャルピング分析（{timeframe}）

### 推奨エントリー
**即座の動きを狙う超短期売買**

- **現在価格**: ${current:,.2f} ({change_pct:+.2f}%)
- **RSI**: {rsi:.1f}

### エントリーポイント
{"🟢 **ロング検討**" if change_pct > 0 and rsi < 60 else "🔴 **ショート検討**" if change_pct < 0 and rsi > 40 else "⏸️ **様子見**"}

**条件:**
- ボラティリティが高い時間帯を狙う
- 1〜5pips程度の小さな値幅を狙う
- 損切りは即座（2〜3pips）

### 具体的戦略
- ✅ サポート: ${support:,.2f} 付近で反発を狙う
- ✅ レジスタンス: ${resistance:,.2f} で利確
- ❌ 損切り: エントリーから±5ドル

### 注意点
- 経済指標発表30分前は避ける
- スプレッドが広がる時間は見送り
- 連続3回負けたら休憩
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

### エントリー戦略
**ロングの場合:**
- エントリー: ${support:,.2f} 付近の押し目
- 損切り: ${support - 20:,.0f}ドル
- 利確: ${resistance:,.2f}ドル（リスクリワード 1:2以上）

**ショートの場合:**
- エントリー: ${resistance:,.2f} 付近の戻り
- 損切り: ${resistance + 20:,.0f}ドル  
- 利確: ${support:,.2f}ドル

### 時間帯別戦略
- 🌅 **9:00-12:00 (東京)**: トレンドフォロー
- 🌆 **16:00-19:00 (欧州)**: ボラティリティ高、注意
- 🌙 **22:00-02:00 (NY)**: 大きな動き、メインセッション

### 今日の注意点
- {"RSI買われすぎ、反落注意" if rsi > 70 else "RSI売られすぎ、反発期待" if rsi < 30 else "RSI中立、トレンドに従う"}
"""
    else:  # スイングトレード
        return f"""
## 📈 スイングトレード分析（{timeframe}）

### 中期トレンド分析
**数日〜数週間保有する戦略**

- **現在価格**: ${current:,.2f} ({change_pct:+.2f}%)
- **RSI**: {rsi:.1f}

### 大局的トレンド
{"🟢 **強気相場** - ロングポジション推奨" if change_pct > 1.0 else "🔴 **弱気相場** - ショートポジション推奨" if change_pct < -1.0 else "🟡 **中立** - 明確なトレンドなし"}

### ポジション戦略
**メインポジション:**
- {"ロング（買い）" if change_pct > 0 else "ショート（売り）"}
- エントリーゾーン: ${support:,.0f}〜${(support+resistance)/2:,.0f}ドル
- 目標価格: ${resistance + 100 if change_pct > 0 else support - 100:,.0f}ドル
- 損切り: ${support - 50:,.0f}ドル

### 週間見通し
- **サポートレベル**: ${support:,.0f}ドル（重要）
- **レジスタンスレベル**: ${resistance:,.0f}ドル
- **次の節目**: $5,000 / $5,100 / $5,200

### リスク管理
- ポジションサイズ: 資金の2〜5%
- 損切りは必須（-2%で自動決済）
- 利確は段階的（50%→5,100、残り50%→5,200）

### ファンダメンタル要因
- ✅ 地政学リスク → 金価格上昇要因
- ✅ インフレ懸念 → 金需要増加
- ⚠️ 米ドル強含み → 金価格下落圧力
- ⚠️ FRB政策 → 利上げなら金下落
"""

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
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 現在価格", f"${current:,.2f}", f"{change:+.2f} ({pct:+.2f}%)")
    with col2:
        rsi_status = "買われすぎ" if rsi > 70 else "売られすぎ" if rsi < 30 else "中立"
        st.metric("📈 RSI", f"{rsi:.1f}", rsi_status)
    with col3:
        st.metric("🔽 サポート", f"${support:,.0f}")
    with col4:
        st.metric("🔼 レジスタンス", f"${resistance:,.0f}")
    
    st.markdown("---")
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='XAUUSD'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA20', line=dict(color='orange', width=2)))
    if len(df) >= 50:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA50', line=dict(color='blue', width=2)))
    fig.add_hline(y=5000, line_dash="dot", line_color="red", annotation_text="5,000")
    fig.update_layout(title=f'📈 XAUUSD {selected_timeframe}チャート', height=600, xaxis_rangeslider_visible=False, template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    tabs = st.tabs(["📊 選択中の分析", "💨 スキャルピング", "📈 デイトレード", "📉 スイング"])
    
    with tabs[0]:
        st.markdown(generate_style_analysis(trade_style, current, pct, rsi, support, resistance, selected_timeframe))
    
    with tabs[1]:
        st.markdown(generate_style_analysis("スキャルピング", current, pct, rsi, support, resistance, selected_timeframe))
    
    with tabs[2]:
        st.markdown(generate_style_analysis("デイトレード", current, pct, rsi, support, resistance, selected_timeframe))
    
    with tabs[3]:
        st.markdown(generate_style_analysis("スイングトレード", current, pct, rsi, support, resistance, selected_timeframe))
    
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
- 取得期間: {period}
""")
st.sidebar.success("✅ パスワード保護")
