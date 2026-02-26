import streamlit as st
import yfinance as yf
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
st.title("💰 XAUUSD リアルタイム分析")

period = st.sidebar.selectbox("期間", ["1d", "5d", "1mo", "3mo"], index=2)

@st.cache_data(ttl=60)
def get_data(p):
    ticker = yf.Ticker("GC=F")
    return ticker.history(period=p)

data = get_data(period)
current = data['Close'].iloc[-1]
previous = data['Close'].iloc[-2]
change = current - previous
pct = (change / previous) * 100

st.metric("現在価格", f"${current:,.2f}", f"{change:+.2f} ({pct:+.2f}%)")

fig = go.Figure()
fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close']))
fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(20).mean(), name='SMA20', line=dict(color='orange')))
fig.add_hline(y=5000, line_dash="dot", line_color="red")
fig.update_layout(height=500, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

if pct > 0.5:
    st.success("📈 強い上昇")
elif pct > 0:
    st.info("📈 上昇")
elif pct < -0.5:
    st.warning("📉 強い下落")
else:
    st.info("📉 下落")

if st.button("🔄 更新"):
    st.cache_data.clear()
    st.rerun()
```

---

## ステップ4：保存を確認
```
1. 貼り付けた後、下にスクロール

2. 「Commit changes」をクリック

3. ポップアップが出たら、もう一度「Commit changes」

4. 完了画面が表示されるまで待つ
   （3〜5秒）

5. app.pyのページに自動で戻る
```

---

## ステップ5：確認
```
1. app.pyのページで行数を確認

2. 何行になっていますか？

正解：約60行

もし145行のままなら、
保存されていません。
```

---

## 📸 または：スクリーンショット

難しければ、以下のスクリーンショットを送ってください：
```
1. GitHubのapp.py編集画面
   （コードが見えている状態）

2. 110〜120行目あたりが見えるように

→ 何が起きているか確認できます
```

---

## 🎯 確認してください

**質問：ステップ2で「全選択→Delete」をした後、画面は空っぽになりましたか？**
```
A. はい、空っぽになった
   → ステップ3のコードを貼り付けてください

B. いいえ、まだ何か残っている
   → もう一度Ctrl+A → Delete

C. よく分からない
   → スクリーンショットを送ってください
