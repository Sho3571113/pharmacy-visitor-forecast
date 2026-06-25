# -----------------------
# 📦 インポート
# -----------------------
import streamlit as st
import pandas as pd
import plotly.express as px
import lightgbm as lgb
import matplotlib.pyplot as plt
import math
from sqlalchemy.orm import sessionmaker
from db_config import engine
from models import VisitData

from authentication import authenticate_user
from lgbforecast import train_lightgbm_model, forecast_visits
from db_service import get_stores, save_visit_data
from db_service import get_stores

stores = get_stores()



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
if st.session_state["user"] is None:

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
    st.header("店舗選択")

    selected_store = st.selectbox(
        "店舗選択",
        stores,
        format_func=lambda x: x.store_name
    )
    # -----------------------
    # ファイルアップロード
    # -----------------------
    if user.role in ["store_manager", "hq_manager", "admin"]:

        st.header("1. 来局データのアップロード")

        uploaded_file = st.file_uploader(
            "CSVファイルを選択（列名: date, visits）",
            type="csv"
    )

    else:
        uploaded_file = None

    # -----------------------
    # 予測条件
    # -----------------------
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

        # DB保存（店舗責任者以上）
        if user.role in ["store_manager", "hq_manager", "admin"]:

            if st.button("DBへ保存"):
                
                saved_count = save_visit_data(
                    df,
                    selected_store.id
                )
                   
                st.success(f"{saved_count}件保存しました")

        required_columns = ["date", "visits"]

        for col in required_columns:
            if col not in df.columns:
                st.error(f"{col} 列がありません")
                st.stop()

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        
        # -----------------------
        # DB確認
        # -----------------------
    if user.role in ["hq_manager", "admin"]:
        
        st.header("DB確認")

        if st.button("DBデータ確認"):

            Session = sessionmaker(bind=engine)
            session = Session()

            rows = session.query(VisitData).filter_by(
                store_id=selected_store.id
            ).all()

            session.close()

            df_db = pd.DataFrame([
                {
                    "store_id": row.store_id,
                    "date": row.date,
                    "visits": row.visits
                }
                for row in rows
            ])

            st.dataframe(df_db.head())
            st.success(f"{len(df_db)}件取得")

        if st.button("DBから予測"):

           Session = sessionmaker(bind=engine)
           session = Session()

           rows = session.query(VisitData).filter_by(
               store_id=selected_store.id
           ).all()

           session.close()

           df_db = pd.DataFrame([
               {
                   "store_id": row.store_id,
                   "date": row.date,
                   "visits": row.visits
               }
                for row in rows
           ])

           df_db["date"] = pd.to_datetime(df_db["date"])
           df_db = df_db.sort_values("date")

           model, le = train_lightgbm_model(df_db)
 
           last_date = df_db["date"].max()

           df_forecast = forecast_visits(
                model,
                le,
                last_date,
                forecast_days
    )

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

        # -----------------------
        # 学習・予測
        # -----------------------
        st.header("3. 予測結果")

        model, le = train_lightgbm_model(df)

        last_date = df["date"].max()

        df_forecast = forecast_visits(
            model,
            le,
            last_date,
            forecast_days
        )
        fig = px.line(
            df_forecast,
            x="date",
            y="predicted_visits",
            title="予測来局者数"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="forecast_chart"
        )
        # -----------------------
        # 予測表
        # -----------------------
        st.subheader("予測表")

        st.dataframe(
            df_forecast.head(10),
            use_container_width=True
        )

        # -----------------------
        # 推奨薬剤師人数
        # -----------------------
        st.header("4. 推奨薬剤師人数")

        def get_staff_suggestion(visits):
            return math.ceil(visits / 25)

        df_staff = df_forecast.copy()

        df_staff["推奨薬剤師数"] = (
            df_staff["predicted_visits"]
            .apply(get_staff_suggestion)
        )

        st.dataframe(
            df_staff[
                ["date", "predicted_visits", "推奨薬剤師数"]
            ],
            use_container_width=True
        )

        # -----------------------
        # 特徴量重要度
        # -----------------------
        st.header("5. 特徴量重要度")

        fig2, ax = plt.subplots(figsize=(8, 5))

        lgb.plot_importance(
            model,
            max_num_features=10,
            ax=ax
        )

        plt.tight_layout()

        st.pyplot(fig2)

    else:
        st.info("CSVファイルをアップロードしてください")