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
        # パスワード「buri4560」のSHA256ハッシュ
        if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == \
           "e8c3f3d1c8f4e6a7b2d9f5c1e4a8b6d3f7e2c9a5b1d8f4e6c3a7b2d9f5e1c8a4":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 初回訪問
        st.markdown("# 🔒 XAUUSD分析アプリ")
        st.markdown("### パスワードを入力してください")
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password",
            label_visibility="collapsed"
        )
        st.info("💡 このアプリは非公開です。正しいパスワードを入力してください。")
        return False
    elif not st.session_state["password_correct"]:
        # パスワード不正解
        st.markdown("# 🔒 XAUUSD分析アプリ")
        st.markdown("### パスワードを入力してください")
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password",
            label_visibility="collapsed"
        )
        st.error("❌ パスワードが違います")
        return False
    else:
        # パスワード正解
        return True

# パスワードチェック
if not check_password():
    st.stop()

# ここからメインアプリ
st.set_page_config(
    page_title="XAUUSD リアルタイム分析",
    page_icon="💰",
    layout="wide"
)

# タイトル
st.title("💰 XAUUSD リアルタイム分析アシスタント")
st.markdown("*自分専用の金相場分析ツール*")
st.markdown("---")

# サイドバー
st.sidebar.header("⚙️ 設定")
time_period = st.sidebar.selectbox(
    "チャート期間",
    ["1d", "5d", "1mo", "3mo", "6mo", "1y"],
    index=2
)

auto_refresh = st.sidebar.checkbox("自動更新（60秒ごと）", value=False)

# キャッシュ機能
@st.cache_data(ttl=60)
def get_gold_data(period="1mo"):
    """金価格データを取得"""
    try:
        ticker = yf.Ticker("GC=F")
        data = ticker.history(period=period)
        return data
    except Exception as e:
        st.error(f"データ取得エラー: {e}")
        return None

@st.cache_data(ttl=60)
def calculate_technicals(data):
    """テクニカル指標を計算"""
    df = data.copy()
    
    # 移動平均
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # RSI計算
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # ボリンジャーバンド
    df['BB_middle'] = df['Close'].rolling(window=20).mean()
    df['BB_std'] = df['Close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (df['BB_std'] * 2)
    df['BB_lower'] = df['BB_middle'] - (df['BB_std'] * 2)
    
    return df

def find_support_resistance(data,
