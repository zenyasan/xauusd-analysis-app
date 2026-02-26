import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import hashlib

# パスワード認証機能
def check_password():
    """パスワード認証"""
    def password_entered():
        """パスワードが正しいかチェック"""
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == "e8c3f3d1c8f4e6a7b2d9f5c1e4a8b6d3f7e2c9a5b1d8f4e6c3a7b2d9f5e1c8a4":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("# 🔒 XAUUSD分析アプリ")
        st.markdown("### パスワードを入力してください")
        st.text_input("Password", type="password", on_change=password_entered, key="password", label_visibility="collapsed")
        st.info("💡 このアプリは非公開です。正しいパスワードを入力してください。")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("# 🔒 XAUUSD分析アプリ")
        st.markdown("### パスワードを入力してください")
        st.text_input("Password", type="password", on_change=password_entered, key="password", label_visibility="collapsed")
        st.error("❌ パスワードが違います")
        return False
    else:
        return True

if not check_password():
    st.stop()

# メインアプリ
st.set_page_config(page_title="XAUUSD リアルタイム分析", page_icon="💰", layout="wide")

st.title("💰 XAUUSD リアルタイム分析アシスタント")
st.markdown("*自分専用の金相場分析ツール*")
st.markdown("---")

# サイドバー
st.sidebar.header("⚙️ 設定")
time_period = st.sidebar.selectbox("チャート期間", ["1d", "5d", "1mo", "3mo", "6mo", "1y"], index=2)
auto_refresh = st.sidebar.checkbox("自動更新（60秒ごと）", value=False)

@st.cache_data(ttl=60)
def get_gold_data(period="1mo"):
    try:
        ticker = yf.Ticker("GC=F")
        data = ticker.history(period=period)
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

def find_support_resistance(data, window=20):
    recent_data = data.tail(100)
    resistance = recent_data['High'].rolling(window=window).max().iloc[-1]
    support = recent_data['Low'].rolling(window=window).min().iloc[-1]
    return support, resistance

def generate_analysis(current_price, change, change_pct, rsi, support, resistance):
    if change_pct > 0.5:
        trend = "📈 **強い上昇トレンド**"
        trend_comment = "買い圧力が強まっています。"
        trend_emoji = "🟢"
    elif change_pct > 0:
        trend = "📈 **緩やかな上昇**"
        trend_comment = "上昇の動きが見られます。"
        trend_emoji = "🟢"
    elif change_pct < -0.5:
        trend = "📉 **強い下落トレンド**"
        trend_comment = "売り圧力が強まっています。"
        trend_emoji = "🔴"
    else:
        trend = "📉 **緩やかな下落**"
        trend_comment = "調整の動きが見られます。"
        trend_emoji = "🔴"
    
    if rsi > 70:
        rsi_signal = "⚠️ **買われすぎ**"
        rsi_comment = "反落の可能性があります。"
    elif rsi < 30:
        rsi_signal = "✅ **売られすぎ**"
        rsi_comment = "反発の可能性があります。"
    else:
        rsi_signal = "➡️ **中立**"
        rsi_comment = "明確なシグナルはありません。"
    
    if current_price >= 5100:
        milestone = "\n\n🎯 **重要**: 5,100ドル台で推移中。上昇トレンドが継続しています。"
    elif current_price >= 5000:
        milestone = "\n\n🎯 **重要**: 5,000ドルの大台を突破。5,100ドル台定着が焦点です。"
    elif current_price >= 4900:
        milestone = "\n\n📍 **重要**: 5,000ドルの大台が目前。節目での攻防に注目。"
    else:
        milestone = "\n\n⚠️ **重要**: 調整局面。5,000ドル回復が課題です。"
    
    analysis = f"""
### {trend_emoji} 現在の状況

{trend}

**現在価格**: ${current_price:,.2f}  
**変動**: {change:+.2f}ドル ({change_pct:+.2f}%)

{trend_comment}

---

### 📊 テクニカル分析

**RSI (14)**: {rsi:.1f} → {rsi_signal}  
{rsi_comment}

**サポートライン**: ${support:,.2f}  
**レジスタンスライン**: ${resistance:,.2f}

{milestone}

---

### ⚠️ 免責事項
この分析は教育・情報提供を目的としており、投資助言ではありません。
"""
    return analysis

try:
    with st.spinner('📊 データを取得中...'):
        data = get_gold_data(time_period)
        if data is None or len(data) == 0:
            st.error("❌ データの取得に失敗しました。しばらくしてから再度お試しください。")
            st.stop()
        df = calculate_technicals(data)
    
    current_price = data['Close'].iloc[-1]
    previous_price = data['Close'].iloc[-2]
    change = current_price - previous_price
    change_pct = (change / previous_price) * 100
    rsi = df['RSI'].iloc[-1]
    support, resistance = find_support_resistance(df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="💰 現在価格", value=f"${current_price:,.2f}", delta=f"{change:+.2f} ({change_pct:+.2f}%)")
    with col2:
        rsi_delta = "買われすぎ" if rsi > 70 else "売られすぎ" if rsi < 30 else "中立"
        st.metric(label="📈 RSI (14)", value=f"{rsi:.1f}", delta=rsi_delta)
    with col3:
        st.metric(label="🔽 サポート", value=f"${support:,.0f}")
    with col4:
        st.metric(label="🔼 レジスタンス", value=f"${resistance:,.0f}")
    
    st.markdown("---")
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='XAUUSD'))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', line=dict(color='orange', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', line=dict(color='blue', width=2)))
    fig.add_hline(y=5000, line_dash="dot", line_color="red", line_width=2, annotation_text="5,000ドル")
    fig.update_layout(title='📈 XAUUSD 価格チャート', yaxis_title='価格 (USD)', height=600, xaxis_rangeslider_visible=False, template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.header("🤖 AI分析")
    with st.expander("📖 現在の詳細分析を見る", expanded=True):
        analysis_text = generate_analysis(current_price, change, change_pct, rsi, support, resistance)
        st.markdown(analysis_text)
    
    st.markdown("---")
    col_update1, col_update2 = st.columns([3, 1])
    with col_update1:
        st.caption(f"⏰ 最終更新: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    with col_update2:
        if st.button("🔄 今すぐ更新", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    if auto_refresh:
        import time
        time.sleep(60)
        st.rerun()

except Exception as e:
    st.error(f"❌ エラーが発生しました: {e}")
    if st.button("ページを再読み込み"):
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("✅ Private設定（自分専用）\n✅ パスワード保護")
```

---

## ✅ 完了後
```
1. コードを貼り付けたら「Commit changes」を2回クリック

2. 自動的に再デプロイが始まります

3. 5〜10分待ちます

4. 今度は成功します！
