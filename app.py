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
# 共通ヘッダー
# -----------------------

def show_header(page_title, stores, user):
    """共通ヘッダーを表示する"""

    title_col, store_col, user_col = st.columns(
        [4, 3, 2]
    )

    with title_col:

        st.markdown(
            f"""
            <div class="header-page-title">
                 {page_title}
            </div>
            """,
            unsafe_allow_html=True
        )

    with store_col:

        selected_store = st.selectbox(
            "選択店舗",
            stores,
            format_func=lambda x: x.store_name,
            key="selected_store",
            label_visibility="collapsed"
        )

    with user_col:

        role_names = {
            "general": "一般ユーザー",
            "store_manager": "店舗責任者",
            "hq_manager": "本部責任者",
            "admin": "システム管理者"
        }

        st.markdown(
            f"""
            <div class="header-user">
                👤 {user.display_name}<br>
                <span>{role_names.get(user.role, user.role)}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    return selected_store

# -----------------------
# ダッシュボード
# -----------------------

def show_dashboard(selected_store):
    """ダッシュボードを表示する"""
 
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
            },
            template="plotly_white"
    )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(
                color="#334155"
            ),
            xaxis=dict(
                gridcolor="#e2e8f0",
                linecolor="#cbd5e1",
                tickfont=dict(color="#334155"),
                title_font=dict(color="#334155")
            ),
            yaxis=dict(
                gridcolor="#e2e8f0",
                linecolor="#cbd5e1",
                tickfont=dict(color="#334155"),
                title_font=dict(color="#334155")
            )
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
# ページ定義
# -----------------------

def show_dashboard_page():
    """ダッシュボードページを表示する"""

    user = st.session_state["user"]

    if user.role in ["hq_manager", "admin"]:
        stores = get_stores()
    else:
        stores = [
            store
            for store in get_stores()
            if store.id == user.store_id
        ]

    if not stores:
        st.error("利用できる店舗がありません。")
        st.stop()

    selected_store = st.session_state.get(
        "selected_store"
    )

    if selected_store is None:
        selected_store = stores[0]
        st.session_state["selected_store"] = selected_store

    show_dashboard(selected_store)


# -----------------------
# ログイン状態
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
    # 利用可能な店舗
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
        st.error("利用できる店舗がありません。")
        st.stop()

    # -----------------------
    # ページ定義
    # -----------------------

    dashboard_page = st.Page(
        show_dashboard_page,
        title="ダッシュボード",
        icon="🏠"
    )

    forecast_page = st.Page(
        "pages/1_📊_来局者予測.py",
        title="来局者予測",
        icon="📊"
    )

    staffing_page = st.Page(
        "pages/2_👥_人員配置.py",
        title="人員配置",
        icon="👥"
    )

    store_page = st.Page(
        "pages/3_🏪_店舗管理.py",
        title="店舗管理",
        icon="🏪"
    )

    user_page = st.Page(
        "pages/4_👤_ユーザー管理.py",
        title="ユーザー管理",
        icon="👤"
    )

    model_page = st.Page(
        "pages/5_⚙️_モデル管理.py",
        title="モデル管理",
        icon="⚙️"
    )

    # -----------------------
    # 権限ごとのページ
    # -----------------------

    if user.role == "general":

        pages = [
            dashboard_page,
            forecast_page,
            staffing_page
        ]

    elif user.role == "store_manager":

        pages = [
            dashboard_page,
            forecast_page,
            staffing_page
        ]

    elif user.role == "hq_manager":

        pages = [
            dashboard_page,
            forecast_page,
            staffing_page,
            model_page
        ]

    else:

        pages = [
            dashboard_page,
            forecast_page,
            staffing_page,
            store_page,
            user_page,
            model_page
        ]

    # -----------------------
    # ナビゲーション
    # -----------------------

    pg = st.navigation(
        pages,
        position="hidden"
    )
    # -----------------------
    # 共通ヘッダー
    # -----------------------

    page_numbers = {
    "ダッシュボード": "①",
    "来局者予測": "②",
    "人員配置": "③",
    "店舗管理": "④",
    "ユーザー管理": "⑤",
    "モデル管理": "⑥"
    }

    selected_store = show_header(
        f'{page_numbers.get(pg.title, "")} {pg.title}',
        stores,
        user
    )

    # -----------------------
    # サイドバー
    # -----------------------

    st.sidebar.title(
        "🏥 来局者予測・人員配置システム"
    )

    st.sidebar.divider()

    st.sidebar.page_link(
        dashboard_page,
        label="ダッシュボード",
        icon="🏠"
    )

    st.sidebar.page_link(
        forecast_page,
        label="来局者予測",
        icon="📊"
    )

    st.sidebar.page_link(
        staffing_page,
        label="人員配置",
        icon="👥"
    )

    if user.role == "admin":

        st.sidebar.page_link(
            store_page,
            label="店舗管理",
            icon="🏪"
        )

        st.sidebar.page_link(
            user_page,
            label="ユーザー管理",
            icon="👤"
        )

    if user.role in ["hq_manager", "admin"]:

        st.sidebar.page_link(
            model_page,
            label="モデル管理",
            icon="⚙️"
        )

    st.sidebar.divider()

    # -----------------------
    # ログアウト
    # -----------------------

    if st.sidebar.button(
        "ログアウト",
        use_container_width=True
    ):

        st.session_state["user"] = None

        st.session_state.pop(
            "selected_store",
            None
        )

        st.rerun()

    # -----------------------
    # ページ表示
    # -----------------------

    pg.run()