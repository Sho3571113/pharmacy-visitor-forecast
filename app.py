# -----------------------
# 📦 インポート
# -----------------------
import streamlit as st
import plotly.express as px
from pathlib import Path
from datetime import date

from authentication import authenticate_user
from db_service import (
    get_stores,
    get_forecast_result,
    get_system_setting
)
from staffing_service import (
    get_staffing,
    get_staff_suggestion
)


# -----------------------
# Streamlit設定
# -----------------------
st.set_page_config(
    page_title="来局者予測・人員配置システム",
    page_icon="🏥",
    layout="wide"
)

# -----------------------
# css設定
# -----------------------

def load_css():
    css_path = Path(__file__).parent / "styles.css"

    with open(css_path, encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


load_css()



# -----------------------
# セッション管理
# -----------------------

if "user" not in st.session_state:
    st.session_state["user"] = None


# -----------------------
# ログイン画面
# -----------------------

def show_login():
    """ログイン画面を表示する"""

    st.markdown(
        '<div class="login-title">来局者予測アプリ</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-description">'
        '過去のデータから来局者を予測できます'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-form-title">ログイン</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-label">ユーザー名</div>',
        unsafe_allow_html=True
    )

    username = st.text_input(
        "ユーザー名",
        label_visibility="collapsed"
    )

    st.markdown(
        '<div class="login-label">パスワード</div>',
        unsafe_allow_html=True
    )

    password = st.text_input(
        "パスワード",
        type="password",
        label_visibility="collapsed"
    )

    if st.button("ログイン", use_container_width=True):

        user = authenticate_user(
            username,
            password
        )

        if user:
            st.session_state["user"] = user
            st.success("ログイン成功")
            st.rerun()

        else:
            st.error(
                "ユーザー名またはパスワードが違います"
            )

# -----------------------
# ダッシュボード
# -----------------------

def show_dashboard(selected_store):
    """ダッシュボードを表示する"""

    # -----------------------
    # ヘッダー
    # -----------------------

     

    title_col, store_col = st.columns([4, 1])

    with title_col:

        st.markdown(
            '<div class="dashboard-title">ダッシュボード</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="dashboard-subtitle">'
            f'{selected_store.store_name} の状況'
            f'</div>',
            unsafe_allow_html=True
        )

    with store_col:

        st.markdown(
            '<div class="store-label">選択店舗</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="store-name">'
            f'{selected_store.store_name}'
            f'</div>',
            unsafe_allow_html=True
        )

    # -----------------------
    # 予測データ取得
    # -----------------------

    df_forecast = get_forecast_result(
        selected_store.id
    )

    if df_forecast.empty:

        st.info(
            "まだ予測データがありません。"
            "「来局者予測」画面から予測を実行してください。"
        )

        return

    # -----------------------
    # 最新の予測データ
    # -----------------------

    latest = df_forecast.iloc[0]

    today = date.today().strftime("%Y年%m月%d日")

    predicted_visits = int(
        latest["predicted_visits"]
    )

    visits_per_pharmacist = get_system_setting(
        "visits_per_pharmacist",
        25
    )

    recommended_staff = get_staff_suggestion(
        predicted_visits,
        visits_per_pharmacist
    )

    # -----------------------
    # 実配置人数
    # -----------------------

    df_staffing = get_staffing(
        selected_store.id
    )

    actual_staff = None

    if not df_staffing.empty:

        matching = df_staffing[
            df_staffing["date"] == latest["date"]
        ]

        if not matching.empty:

            actual_staff = int(
                matching.iloc[0]["staff_count"]
            )

    if actual_staff is None:
        actual_staff = recommended_staff

    # -----------------------
    # 人員状況
    # -----------------------

    shortage = (
        recommended_staff
        - actual_staff
    )

    # -----------------------
    # KPI
    # -----------------------
    st.subheader(f"今日の状況（{today}）")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">予測来局者数</div>
                <div class="kpi-value">
                    {predicted_visits}
                    <span class="kpi-unit">人</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">推奨薬剤師数</div>
                <div class="kpi-value">
                    {recommended_staff}
                    <span class="kpi-unit">人</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col3:

        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">実配置人数</div>
                <div class="kpi-value">
                    {actual_staff}
                    <span class="kpi-unit">人</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col4:

        if shortage > 0:

            status_text = f"{shortage}人不足"
            status_class = "status-warning"

        elif shortage < 0:

            status_text = f"{abs(shortage)}人余力"
            status_class = "status-normal"

        else:

            status_text = "適正"
            status_class = "status-normal"


        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">人員状況</div>
                <div class="kpi-value {status_class}">
                    {status_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

   
    # -----------------------
    # 区切り
    # -----------------------

    st.divider()

    # -----------------------
    # グラフ
    # -----------------------

    graph_col, info_col = st.columns([2.5, 1])

    with graph_col:

        st.subheader("📈 今後の来局者数予測")

        fig = px.line(
            df_forecast,
            x="date",
            y="predicted_visits",
            markers=True,
            labels={
                "date": "日付",
                "predicted_visits": "予測来局者数"
            }
        )

        fig.update_layout(
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            height=400
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -----------------------
    # 今日のコメント
    # -----------------------

    with info_col:

        st.subheader("💡 今日の状況")

        if shortage > 0:

            st.warning(
                f"推奨人数に対して "
                f"{shortage}人不足しています。"
            )

        elif shortage < 0:

            st.success(
                f"推奨人数に対して "
                f"{abs(shortage)}人の余力があります。"
            )

        else:

            st.success(
                "推奨人数と実配置人数が一致しています。"
            )

        st.subheader("ℹ️ システム情報")

        st.write(
            f"薬剤師1人あたりの担当来局者数："
            f"**{visits_per_pharmacist}人**"
        )


# -----------------------
# ログイン状態による画面切り替え
# -----------------------

if st.session_state["user"] is None:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    show_login()

else:

    user = st.session_state["user"]

    # -----------------------
    # サイドバー
    # -----------------------

    st.sidebar.title(
        "🏥 来局者予測・人員配置システム"
    )

    st.sidebar.divider()

    role_names = {
        "general": "一般ユーザー",
        "store_manager": "店舗責任者",
        "hq_manager": "本部責任者",
        "admin": "システム管理者"
    }

    st.sidebar.write(
        f"👤 **{user.display_name}**"
    )

    st.sidebar.caption(
        role_names.get(user.role, user.role)
    )

    if st.sidebar.button(
        "ログアウト",
        use_container_width=True
    ):

        st.session_state["user"] = None
        st.rerun()

    # -----------------------
    # 店舗取得
    # -----------------------

    if user.role in ["hq_manager", "admin"]:

        stores = get_stores()

    else:

        stores = [
            store
            for store in get_stores()
            if store.id == user.store_id
        ]

    if not stores:

        st.error(
            "利用できる店舗がありません。"
        )

        st.stop()

    # -----------------------
    # 店舗選択
    # -----------------------

    st.sidebar.subheader("店舗")

    selected_store = st.sidebar.selectbox(
        "店舗選択",
        stores,
        format_func=lambda x: x.store_name,
        label_visibility="collapsed"
    )

    # -----------------------
    # ダッシュボード表示
    # -----------------------

    show_dashboard(selected_store)