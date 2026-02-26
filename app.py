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
           "4e42de48f9cdf95d8cbf5ad17f11a63601120eb1cdaa35eae088bb75196e4a67":
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

def find_support_resistance(data, window=20):
    """サポート・レジスタンスを検出"""
    recent_data = data.tail(100)
    resistance = recent_data['High'].rolling(window=window).max().iloc[-1]
    support = recent_data['Low'].rolling(window=window).min().iloc[-1]
    return support, resistance

def generate_simple_analysis(current_price, change, change_pct, rsi, support, resistance):
    """シンプルな分析テキストを生成"""
    
    # トレンド判定
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
    
    # RSI判定
    if rsi > 70:
        rsi_signal = "⚠️ **買われすぎ**"
        rsi_comment = "反落の可能性があります。"
    elif rsi < 30:
        rsi_signal = "✅ **売られすぎ**"
        rsi_comment = "反発の可能性があります。"
    else:
        rsi_signal = "➡️ **中立**"
        rsi_comment = "明確なシグナルはありません。"
    
    # 5,000ドル節目
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

### 💡 トレード戦略（参考）

"""
    
    if change_pct > 0:
        analysis += f"""
**ロング（買い）を検討する場合:**
- ✅ エントリー: ${support:,.0f}付近まで押したら検討
- ❌ 損切り: ${support - 30:,.0f}ドル（サポート割れ）
- 🎯 利確目標: ${resistance:,.0f}ドル

**注意点:**
- 急騰後は利益確定売りに警戒
- RSIが70超えなら様子見推奨
"""
    else:
        analysis += f"""
**ショート（売り）を検討する場合:**
- ✅ エントリー: ${resistance:,.0f}付近まで戻したら検討
- ❌ 損切り: ${resistance + 30:,.0f}ドル（レジスタンス超え）
- 🎯 利確目標: ${support:,.0f}ドル

**注意点:**
- 急落後は反発の可能性に注意
- RSIが30未満なら様子見推奨
"""
    
    analysis += """

---

### ⚠️ 免責事項
この分析は教育・情報提供を目的としており、投資助言ではありません。  
トレードは必ず自己責任で行ってください。
"""
    
    return analysis

# メイン処理
try:
    # データ取得
    with st.spinner('📊 データを取得中...'):
        data = get_gold_data(time_period)
        
        if data is None or len(data) == 0:
            st.error("❌ データの取得に失敗しました。しばらくしてから再度お試しください。")
            st.stop()
        
        df = calculate_technicals(data)
    
    # 現在価格
    current_price = data['Close'].iloc[-1]
    previous_price = data['Close'].iloc[-2]
    change = current_price - previous_price
    change_pct = (change / previous_price) * 100
    
    # テクニカル指標
    rsi = df['RSI'].iloc[-1]
    support, resistance = find_support_resistance(df)
    
    # 上部に現在価格を大きく表示
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 現在価格",
            value=f"${current_price:,.2f}",
            delta=f"{change:+.2f} ({change_pct:+.2f}%)"
        )
    
    with col2:
        rsi_delta = "買われすぎ" if rsi > 70 else "売られすぎ" if rsi < 30 else "中立"
        st.metric(
            label="📈 RSI (14)",
            value=f"{rsi:.1f}",
            delta=rsi_delta
        )
    
    with col3:
        st.metric(
            label="🔽 サポート",
            value=f"${support:,.0f}"
        )
    
    with col4:
        st.metric(
            label="🔼 レジスタンス",
            value=f"${resistance:,.0f}"
        )
    
    st.markdown("---")
    
    # チャート作成
    fig = go.Figure()
    
    # ローソク足
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='XAUUSD',
        increasing_line_color='#00ff00',
        decreasing_line_color='#ff0000'
    ))
    
    # 移動平均線
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA_20'],
        name='SMA 20',
        line=dict(color='orange', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA_50'],
        name='SMA 50',
        line=dict(color='blue', width=2)
    ))
    
    # ボリンジャーバンド
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['BB_upper'],
        name='BB Upper',
        line=dict(color='rgba(128,128,128,0.3)', width=1, dash='dash'),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['BB_lower'],
        name='BB Lower',
        line=dict(color='rgba(128,128,128,0.3)', width=1, dash='dash'),
        fill='tonexty',
        fillcolor='rgba(128,128,128,0.1)',
        showlegend=False
    ))
    
    # 重要ライン
    fig.add_hline(y=5000, line_dash="dot", line_color="red", line_width=2,
                 annotation_text="5,000ドル", annotation_position="right")
    
    fig.update_layout(
        title='📈 XAUUSD 価格チャート',
        yaxis_title='価格 (USD)',
        xaxis_title='日時',
        height=600,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        template='plotly_dark'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # RSIチャート
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(
        x=df.index,
        y=df['RSI'],
        name='RSI',
        line=dict(color='purple', width=2),
        fill='tozeroy',
        fillcolor='rgba(128,0,128,0.1)'
    ))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="買われすぎ (70)")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="売られすぎ (30)")
    fig_rsi.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="中立 (50)")
    fig_rsi.update_layout(
        title='📊 RSI (Relative Strength Index)',
        yaxis_title='RSI',
        height=250,
        showlegend=False,
        template='plotly_dark'
    )
    
    st.plotly_chart(fig_rsi, use_container_width=True)
    
    st.markdown("---")
    
    # 分析セクション
    st.header("🤖 AI分析（ペルソナA）")
    
    with st.expander("📖 現在の詳細分析を見る", expanded=True):
        analysis_text = generate_simple_analysis(
            current_price, change, change_pct, rsi, support, resistance
        )
        st.markdown(analysis_text)
    
    # 質問セクション
    st.markdown("---")
    st.header("💬 質問してください")
    st.info("""
    **💡 現在は無料版です**
    
    上記の自動分析をご参照ください。
    
    より高度なAI解説機能（ペルソナAでの対話）を追加したい場合は、
    Claude APIキーを設定することで利用可能になります。
    
    **追加で必要な費用**: 月$3〜15程度（使った分だけ）
    """)
    
    # 更新情報
    st.markdown("---")
    col_update1, col_update2 = st.columns([3, 1])
    
    with col_update1:
        st.caption(f"⏰ 最終更新: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        st.caption("💾 データは60秒間キャッシュされます")
    
    with col_update2:
        if st.button("🔄 今すぐ更新", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # 自動更新
    if auto_refresh:
        import time
        time.sleep(60)
        st.rerun()

except Exception as e:
    st.error(f"❌ エラーが発生しました: {e}")
    st.info("🔄 ページを再読み込みしてください。")
    if st.button("ページを再読み込み"):
        st.rerun()

# サイドバーに情報
st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 使い方")
st.sidebar.info("""
1. チャートと指標を確認
2. 自動分析を読む
3. 必要に応じてデータ更新

**データ更新頻度**:
- 自動: 60秒ごとにキャッシュ更新
- 手動: 更新ボタンで即時更新
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ 注意事項")
st.sidebar.warning("""
- 価格は約15分の遅延があります
- 投資判断は必ず自己責任で
- このツールは教育目的です
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔐 セキュリティ")
st.sidebar.success("""
✅ Private設定（自分専用）
✅ パスワード保護
✅ 外部からアクセス不可
""")

st.sidebar.markdown("---")
st.sidebar.caption("Made with ❤️ by Claude")
