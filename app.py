# -----------------------
# 📦 インポート
# -----------------------
import streamlit as st
import plotly.express as px

from authentication import authenticate_user
from db_service import get_stores, get_forecast_result,get_system_setting
from staffing_service import get_staffing, get_staff_suggestion
# -----------------------
# Streamlit設定
# -----------------------
st.set_page_config(
    page_title="来局者予測システム",
    layout="centered"
)


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

    st.title("🔐 ログイン")

    username = st.text_input("ユーザー名")

    password = st.text_input(
        "パスワード",
        type="password"
    )

    if st.button("ログイン"):

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

    st.title("🏠 ダッシュボード")

    st.caption(
        f"{selected_store.store_name} の状況"
    )

    df_forecast = get_forecast_result(
        selected_store.id
    )

    if df_forecast.empty:

        st.info(
            "まだ予測データがありません。"
            "来局者予測画面から予測を実行してください。"
        )

        return

    # -----------------------
    # 最新の予測データ
    # -----------------------

    latest = df_forecast.iloc[0]

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

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "予測来局者数",
            f"{predicted_visits}人"
        )

    with col2:

        st.metric(
            "推奨薬剤師数",
            f"{recommended_staff}人"
        )

    with col3:

        st.metric(
            "実配置人数",
            f"{actual_staff}人"
        )

    with col4:

        if shortage > 0:

            st.metric(
                "人員状況",
                f"{shortage}人不足"
            )

        elif shortage < 0:

            st.metric(
                "人員状況",
                f"{abs(shortage)}人余力"
            )

        else:

            st.metric(
                "人員状況",
                "適正"
            )

    # -----------------------
    # 予測グラフ
    # -----------------------

    st.subheader(
        "今後の来局者数予測"
    )

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

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# -----------------------
# ログイン状態による画面切り替え
# -----------------------

if st.session_state["user"] is None:

    show_login()

else:

    user = st.session_state["user"]

    # -----------------------
    # サイドバー
    # -----------------------

    st.sidebar.header("ユーザー情報")

    role_names = {
        "general": "一般ユーザー",
        "store_manager": "店舗責任者",
        "hq_manager": "本部責任者",
        "admin": "システム管理者"
    }

    st.sidebar.write(
        f"氏名: {user.display_name}"
    )

    st.sidebar.write(
        f"権限: {role_names.get(user.role, user.role)}"
    )

    if st.sidebar.button("ログアウト"):

        st.session_state["user"] = None
        st.rerun()

    # -----------------------
    # 店舗選択
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

    selected_store = st.selectbox(
        "店舗選択",
        stores,
        format_func=lambda x: x.store_name
    )

    # -----------------------
    # ダッシュボード表示
    # -----------------------

    show_dashboard(selected_store)