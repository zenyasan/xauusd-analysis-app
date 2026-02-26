import streamlit as st

st.set_page_config(page_title="カラーパレット", page_icon="🎨", layout="wide")

st.title("🎨 XAUUSD分析アプリ - カラーパレット選択")
st.markdown("### お好みの色を選んでください")

color_schemes = {
    "現在のデザイン（エメラルドグリーン寄り）": {
        "primary": "#00d9ff",
        "secondary": "#7b2ff7",
        "accent": "#f107d4",
        "bg_from": "#0a0e27",
        "bg_to": "#1a1d3a"
    },
    "案1：ディープブルー（落ち着いた青）": {
        "primary": "#0066ff",
        "secondary": "#4d94ff",
        "accent": "#8b2ff7",
        "bg_from": "#0a0e27",
        "bg_to": "#1a1d3a"
    },
    "案2：エレクトリックブルー（明るい青）": {
        "primary": "#007bff",
        "secondary": "#0099ff",
        "accent": "#6c2ff7",
        "bg_from": "#0a0e27",
        "bg_to": "#1a1d3a"
    },
    "案3：ロイヤルブルー（王道の青）": {
        "primary": "#0052cc",
        "secondary": "#0080ff",
        "accent": "#7b2ff7",
        "bg_from": "#0a0e27",
        "bg_to": "#1a1d3a"
    },
    "案4：ネオンブルー（鮮やかな青）": {
        "primary": "#0080ff",
        "secondary": "#00aaff",
        "accent": "#8b2ff7",
        "bg_from": "#0a0e27",
        "bg_to": "#1a1d3a"
    },
    "案5：スカイブルー（明るめ青）": {
        "primary": "#1E90FF",
        "secondary": "#4da6ff",
        "accent": "#7b2ff7",
        "bg_from": "#0a0e27",
        "bg_to": "#1a1d3a"
    }
}

for scheme_name, colors in color_schemes.items():
    st.markdown(f"## {scheme_name}")
    
    # カラーパレット表示
    cols = st.columns(5)
    
    with cols[0]:
        st.markdown(f"""
        <div style="
            background: {colors['primary']};
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            color: white;
            font-weight: bold;
            box-shadow: 0 0 30px {colors['primary']}80;
        ">
            メインカラー<br>{colors['primary']}
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
        <div style="
            background: {colors['secondary']};
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            color: white;
            font-weight: bold;
            box-shadow: 0 0 30px {colors['secondary']}80;
        ">
            セカンダリ<br>{colors['secondary']}
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
        <div style="
            background: {colors['accent']};
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            color: white;
            font-weight: bold;
            box-shadow: 0 0 30px {colors['accent']}80;
        ">
            アクセント<br>{colors['accent']}
        </div>
        """, unsafe_allow_html=True)
    
    with cols[3]:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            color: white;
            font-weight: bold;
            box-shadow: 0 0 30px {colors['primary']}60;
        ">
            グラデーション
        </div>
        """, unsafe_allow_html=True)
    
    with cols[4]:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {colors['bg_from']}, {colors['bg_to']});
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            color: {colors['primary']};
            font-weight: bold;
            border: 2px solid {colors['primary']};
        ">
            背景イメージ
        </div>
        """, unsafe_allow_html=True)
    
    # プレビューカード
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {colors['primary']}20, {colors['secondary']}20);
        backdrop-filter: blur(10px);
        border: 1px solid {colors['primary']}50;
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 8px 32px {colors['primary']}40;
    ">
        <h3 style="color: {colors['primary']}; margin: 0;">💰 現在価格</h3>
        <h1 style="color: {colors['primary']}; margin: 10px 0; font-size: 2.5rem;">$5,108.50</h1>
        <p style="color: {colors['secondary']};">+25.30 (+0.49%)</p>
        
        <div style="margin-top: 20px;">
            <button style="
                background: linear-gradient(135deg, {colors['primary']}40, {colors['secondary']}40);
                color: {colors['primary']};
                border: 2px solid {colors['primary']};
                padding: 12px 30px;
                border-radius: 12px;
                font-weight: bold;
                cursor: pointer;
            ">🔄 更新</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

st.markdown("## 📝 お好みのデザインを選んだら...")
st.info("選んだデザインの番号を教えてください。すぐに本番コードを修正します！")
