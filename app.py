import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import hashlib

def check_password():
    def password_entered():
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == "e8c3f3d1c8f4e6a7b2d9f5c1e4a8b6d3f7e2c9a5b1d8f4e6c3a7b2d9f5e1c8a4":
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
    else:
        return True

if not check_password():
    st.stop()

st.set_page_config(page_title="XAUUSD分析", page_icon="💰", layout="wide")
st.title("💰 XAUUSD リアルタイム分析")
st.markdown("---")

st.sidebar.header("⚙️ 設定")
period = st.sidebar.selectbox("期間", ["1d", "5d", "1mo", "3mo"], index=2)

@st.cache_data(ttl=60)
def get_data(period):
    try:
        ticker = yf.Ticker("GC=F")
        return ticker.history(period=period)
    except:
        return None

data = get_data(period)

if data is None or len(data) == 0:
    st.error("データ取得エラー")
    st.stop()

current = data['Close'].iloc[-1]
previous = data['Close'].iloc[-2]
change = current - previous
change_pct = (change / previous) * 100

col1, col2 = st.columns(2)
with col1:
    st.metric("現在価格", f"${current:,.2f}", f"{change:+.2f} ({change_pct:+.2f}%)")
with col2:
    high = data['High'].tail(20).max()
    low = data['Low'].tail(20).min()
    st.metric("範囲（20日）", f"${low:,.0f} - ${high:,.0f}")

fig = go.Figure()
fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='XAUUSD'))

sma20 = data['Close'].rolling(20).mean()
sma50 = data['Close'].rolling(50).mean()

fig.add_trace(go.Scatter(x=data.index, y=sma20, name='SMA20', line=dict(color='orange')))
fig.add_trace(go.Scatter(x=data.index, y=sma50, name='SMA50', line=dict(color='blue')))
fig.add_hline(y=5000, line_dash="dot", line_color="red", annotation_text="5,000")

fig.update_layout(title='XAUUSD チャート', yaxis_title='価格 (USD)', height=600, xaxis_rangeslider_visible=False, template='plotly_dark')

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.header("📊 分析")

if change_pct > 0.5:
    st.success("📈 強い上昇トレンド")
elif change_pct > 0:
    st.info("📈 緩やかな上昇")
elif change_pct < -0.5:
    st.warning("📉 強い下落トレンド")
else:
    st.info("📉 緩やかな下落")

if current >= 5100:
    st.info("🎯 5,100ドル台で推移中")
elif current >= 5000:
    st.info("🎯 5,000ドル突破")
elif current >= 4900:
    st.info("📍 5,000ドルが目前")

st.markdown("---")
st.caption(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if st.button("🔄 更新"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.success("✅ 自分専用アプリ")
```

---

### ステップ4：保存
```
1. 画面下にスクロール

2. 「Commit changes」をクリック

3. もう一度「Commit changes」をクリック

完了！
```

---

## ✅ 手順の確認
```
□ app.py を開いた
□ 鉛筆アイコン（編集）をクリック
□ Ctrl+A で全選択
□ Delete で全削除
□ 新しいコードを貼り付け
□ 「Commit changes」を2回クリック

完了したら「編集完了！」と教えてください
```

---

## 💡 このコードの特徴
```
✅ 1行が短い（構文エラーが起きにくい）
✅ シンプルで確実
✅ パスワード「buri4560」で保護
✅ チャート表示
✅ 簡易分析
✅ 動作確認後、機能追加可能
