# -----------------------
# 📦 インポート
# -----------------------
import streamlit as st
import pandas as pd
import plotly.express as px
import lightgbm as lgb
import matplotlib.pyplot as plt
import math

from authentication import authenticate_user
from db_service import get_users, get_stores, save_visit_data, get_visit_data, create_user, get_forecast_result, add_store

from forecast_service import ( forecast_from_db, train_model_from_db )

from staffing_service import (
    save_staffing,
    get_staffing
)


# -----------------------
#共通関数
# -----------------------
def get_staff_suggestion(visits):
    return math.ceil(visits / 25)


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

if "df_forecast" not in st.session_state:
    st.session_state["df_forecast"] = None

if "model" not in st.session_state:
    st.session_state["model"] = None

if "db_data" not in st.session_state:
    st.session_state["db_data"] = None

if "df_staff" not in st.session_state:
    st.session_state["df_staff"] = None

# -----------------------
# 関数
# -----------------------
def show_login():
    """ログイン画面を表示する"""

    st.title("🔐 ログイン")

    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")

    if st.button("ログイン"):

        user = authenticate_user(username, password)

        if user:
            st.session_state["user"] = user
            st.success("ログイン成功")
            st.rerun()
        else:
            st.error("ユーザー名またはパスワードが違います")

def show_csv_upload(user):
    """CSVアップロード画面を表示する"""

    if user.role in ["store_manager", "hq_manager", "admin"]:

        st.header("1. 来局データのアップロード")

        uploaded_file = st.file_uploader(
            "CSVファイルを選択（列名: date, visits）",
            type="csv"
        )

    else:
        uploaded_file = None

    return uploaded_file

def show_db_data(user, selected_store):
    """DBデータ確認画面を表示する"""

    if user.role in ["store_manager", "hq_manager", "admin"]:

        st.header("DB確認")

        if st.button("DBデータ確認"):
            st.session_state["db_data"] = get_visit_data(
                selected_store.id
            )

        if st.session_state["db_data"] is not None:
            st.dataframe(
                st.session_state["db_data"],
                use_container_width=True
            )

def run_forecast(user, selected_store, forecast_days):
    """DBから来局者予測を実行する"""
    if user.role  in ["hq_manager", "admin"]:

        if st.button("DBから予測"):

            df_forecast, model = forecast_from_db(
            selected_store.id,
            forecast_days
        )
            if df_forecast is None:
                st.warning("モデルが未学習、または予測できるデータがありません。")
                return


            st.session_state["df_forecast"] = df_forecast
            st.session_state["model"] = model
            st.session_state["df_staff"] = None

        
def show_forecast_result(selected_store):
    """予測結果を表示する"""
    df_forecast = get_forecast_result(selected_store.id)
    if df_forecast.empty:
        return

   

    df_forecast = get_forecast_result(selected_store.id)

    fig = px.line(
        df_forecast,
        x="date",
        y="predicted_visits",
        title="DBデータによる予測"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="db_forecast_chart"
    )

    st.subheader("予測表")

    st.dataframe(
        df_forecast.head(10),
        use_container_width=True
    )

def show_staffing(selected_store):
    """スタッフ配置画面を表示する"""

    st.header("4. 推奨薬剤師人数")

    if st.session_state["df_staff"] is None:
        df_staff = st.session_state["df_forecast"].copy()

        df_staff["推奨薬剤師数"] = (
            df_staff["predicted_visits"]
            .apply(get_staff_suggestion)
        )

        df_staff["実配置人数"] = df_staff["推奨薬剤師数"]

        saved_staff = get_staffing(selected_store.id)

        if not saved_staff.empty:
            for _, row in saved_staff.iterrows():
                df_staff.loc[
                    df_staff["date"] == row["date"],
                    "実配置人数"
                ] = row["staff_count"]

        st.session_state["df_staff"] = df_staff

    edited_df = st.data_editor(
        st.session_state["df_staff"][
            ["date", "predicted_visits", "推奨薬剤師数", "実配置人数"]
        ],
        use_container_width=True,
        hide_index=True,
        key="staff_editor"
    )

    st.session_state["df_staff"]["実配置人数"] = edited_df["実配置人数"]

    if st.button("実配置人数を保存"):

        for _, row in st.session_state["df_staff"].iterrows():
            save_staffing(
                selected_store.id,
                row["date"],
                row["実配置人数"]
            )

        st.success("実配置人数を保存しました")

def show_feature_importance():
    """特徴量重要度を表示する"""

    st.header("5. 特徴量重要度")

    fig2, ax = plt.subplots(figsize=(8, 5))

    lgb.plot_importance(
        st.session_state["model"],
        max_num_features=10,
        ax=ax
    )

    plt.tight_layout()

    st.pyplot(fig2)


# -----------------------
# ログイン画面(関数)
# -----------------------
if st.session_state["user"] is None:
    show_login()

# -----------------------
# ログイン後画面
# -----------------------
else:

    user = st.session_state["user"]

    # サイドバー
    st.sidebar.header("ユーザー情報")
    role_names = {
    "general": "一般ユーザー",
    "store_manager": "店舗責任者",
    "hq_manager": "本部責任者",
    "admin": "システム管理者"
    }
    st.sidebar.write(f"氏名: {user.display_name}")
    st.sidebar.write(f"権限: {role_names.get(user.role, user.role)}")

    if st.sidebar.button("ログアウト"):
        st.session_state["user"] = None
        st.rerun()

    # メイン画面
    st.title("📈 来局者予測システム")
    st.write("CSVをアップロードして来局者数を予測します")

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

    st.header("店舗選択")

    selected_store = st.selectbox(
        "店舗選択",
        stores,
        format_func=lambda x: x.store_name
    )
    # -----------------------
    # ファイルアップロード(関数)
    # -----------------------
    uploaded_file = show_csv_upload(user)

    # -----------------------
    # 予測条件
    # -----------------------
    if user.role in ["hq_manager", "admin"]:

        st.header("モデル管理")

        if st.button("モデル学習"):

            success = train_model_from_db(selected_store.id)

            if success:
                st.success("モデル学習が完了しました。")
            else:
                st.warning("学習できるデータがありません。")

    st.header("2. 予測条件の設定")

    col1, col2 = st.columns(2)

    with col1:
        forecast_days = st.slider(
            "予測日数",
            7,
            90,
            30
        )

    with col2:
        patient_type = st.radio(
            "患者タイプ",
            ["全体", "新患", "継続"]
        )

    # -----------------------
    # 予測処理
    # -----------------------
    if uploaded_file:

        df = pd.read_csv(uploaded_file)

        st.subheader("CSVデータ確認")
        st.dataframe(df.head())

        if st.button("DBへ保存"):
                
            try:
                saved_count = save_visit_data(
                    df,
                    selected_store.id
                )
                   
                st.success(f"{saved_count}件保存しました")
            
            except ValueError as e:
                st.error(str(e))
        
        # -----------------------
        # DB確認(関数)
        # -----------------------
    show_db_data(user, selected_store)

        # -----------------------
        # DBから予測(関数)
        # -----------------------

    run_forecast(user, selected_store, forecast_days)

        # -----------------------
        # 製図以下
        # -----------------------
    if st.session_state["df_forecast"] is not None:
            show_forecast_result(selected_store)

        # -----------------------
        #　推奨人数、実配置人数
        # -----------------------  
            show_staffing(selected_store)

        # -----------------------
        # 特徴量重要度
        # -----------------------
            show_feature_importance()

#ユーザー管理
    if user.role == "admin":
        df_users = get_users()
        st.dataframe(df_users)
        stores = get_stores()
        st.header("店舗管理")

        store_name = st.text_input("店舗名")

        if st.button("店舗追加"):
            if not store_name:
                st.error("店舗名を入力してください")
            else:
                result = add_store(store_name)

                if result:
                    st.success("店舗を追加しました")
                else:
                    st.warning("その店舗は既に存在します")


    # ユーザー追加フォーム
        username = st.text_input("ユーザー名")
        display_name = st.text_input("表示名")
        password = st.text_input(
        "パスワード",
        type="password"
        )
        role = st.selectbox(
        "権限",
        [
            "general",
            "store_manager",
            "hq_manager",
            "admin",
        ],
        )
    
        if role in ["general", "store_manager"]:
            selected_store = st.selectbox(
            "店舗",
            stores,
            format_func=lambda x: x.store_name
    )
            store_id = selected_store.id
        else:
            store_id = None

        if st.button("ユーザー登録"):
            try:
                create_user(
                username,
                display_name,
                password,
                role,
                store_id,
            )
                st.success("ユーザーを登録しました。")

            except ValueError as e:
                st.error(str(e))
    
    