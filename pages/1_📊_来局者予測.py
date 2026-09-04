import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from db_service import (
    get_stores,
    save_visit_data,
    get_visit_data,
    get_forecast_result
)
from forecast_service import forecast_from_db

def load_css():
    css_path = Path(__file__).parent.parent / "styles.css"

    with open(css_path, encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


load_css()

user = st.session_state.get("user")

if "df_forecast" not in st.session_state:
    st.session_state["df_forecast"] = None

if "db_data" not in st.session_state:
    st.session_state["db_data"] = None

if "model" not in st.session_state:
    st.session_state["model"] = None

if user is None:
    st.warning("ログインしてください。")
    st.stop()

st.markdown(
    '<div class="forecast-title">📊 来局者予測</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="forecast-subtitle">'
    '過去の来局データをもとに、今後の来局者数を予測します'
    '</div>',
    unsafe_allow_html=True
)

if user.role in ["hq_manager", "admin"]:
    stores = get_stores()
else:
    stores = [
        store
        for store in get_stores()
        if store.id == user.store_id
    ]

selected_store = st.selectbox(
    "店舗選択",
    stores,
    format_func=lambda x: x.store_name
)

if user.role in ["store_manager", "hq_manager", "admin"]:

    st.subheader("来局データのアップロード")

    uploaded_file = st.file_uploader(
        "CSVファイルを選択（列名: date, visits）",
        type="csv"
    )

else:
    uploaded_file = None


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

if user.role in ["store_manager", "hq_manager", "admin"]:

    st.subheader("DBデータ確認")

    if st.button("DBデータ確認"):

        st.session_state["db_data"] = get_visit_data(
            selected_store.id
        )

    if st.session_state.get("db_data") is not None:

        st.dataframe(
            st.session_state["db_data"],
            use_container_width=True
        )

st.subheader("予測条件")

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

if user.role in ["hq_manager", "admin"]:

    if st.button("DBから予測"):

        df_forecast, model = forecast_from_db(
            selected_store.id,
            forecast_days
        )

        if df_forecast is None:
            st.warning(
                "モデルが未学習、または予測できるデータがありません。"
            )
        else:
            st.session_state["df_forecast"] = df_forecast
            st.session_state["model"] = model

            st.success("予測が完了しました。")


if st.session_state["df_forecast"] is not None:

    st.subheader("予測結果")

    df_display = st.session_state["df_forecast"].head(10).copy()

    df_display["date"] = pd.to_datetime(
        df_display["date"]
    ).dt.date

    df_display = df_display.rename(
        columns={
            "date": "日付",
            "predicted_visits": "予測来局者数"
        }
    )

    st.dataframe(
        df_display,
        use_container_width=True
    )

    st.subheader("来局者数予測")

    df_forecast = st.session_state["df_forecast"]

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