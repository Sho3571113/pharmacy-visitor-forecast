import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from db_service import (
    save_visit_data,
    # get_visit_data,
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

#if "db_data" not in st.session_state:
#    st.session_state["db_data"] = None

if "model" not in st.session_state:
    st.session_state["model"] = None

if user is None:
    st.warning("ログインしてください。")
    st.stop()

selected_store = st.session_state["selected_store"]

with st.container(key="forecast-control"):


    col1, col2 = st.columns([2, 2], vertical_alignment="bottom")

    with col1:
        forecast_days = st.selectbox(
            "予測期間",
            [7, 14, 30, 60, 90],
            index=2,
            format_func=lambda x: f"{x}日間"
        )

    with col2:
        predict_button = st.button(
            "予測を実行",
            use_container_width=True
        )

if user.role in ["store_manager", "hq_manager", "admin"]:

    with st.container(key="upload-card"):

        st.markdown(
            '<div class="forecast-section-title">'
            '来局データのアップロード'
            '</div>',
            unsafe_allow_html=True
        )

        uploaded_file = st.file_uploader(
            "CSVファイルを選択（列名: date, visits）",
            type="csv"
        )

else:
    uploaded_file = None


if uploaded_file:

    df = pd.read_csv(uploaded_file)

    with st.container(key="csv-preview-card"):

        st.markdown(
            '<div class="forecast-section-title">'
            'CSVデータ確認'
            '</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            df.head(10),
            use_container_width=True,
            hide_index=True
        )

        if st.button("DBへ保存"):

            try:
                saved_count = save_visit_data(
                    df,
                    selected_store.id
                )

                st.success(f"{saved_count}件保存しました")

            except ValueError as e:
                st.error(str(e))

#if user.role in ["store_manager", "hq_manager", "admin"]:
#
#    st.subheader("DBデータ確認")
#
#    if st.button("DBデータ確認"):
#
#       st.session_state["db_data"] = get_visit_data(
#            selected_store.id
#       )
#
#   if st.session_state.get("db_data") is not None:
#
#       st.dataframe(
#          st.session_state["db_data"],
#          use_container_width=True
#       )


if user.role in ["hq_manager", "admin"]:

    if predict_button:

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

    df_forecast = st.session_state["df_forecast"]

    df_display = df_forecast.head(10).copy()

    df_display["date"] = pd.to_datetime(
        df_display["date"]
    ).dt.date

    df_display = df_display.rename(
        columns={
            "date": "日付",
            "predicted_visits": "予測来局者数"
        }
    )

    st.markdown(
        '<div class="forecast-section-title">予測結果</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([2, 1])

    with col1:

        st.markdown(
            '<div class="forecast-card-title">'
            '来局者数予測グラフ'
            '</div>',
            unsafe_allow_html=True
        )

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

    with col2:

        st.markdown(
            '<div class="forecast-card-title">'
            '予測結果一覧'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            df_display.to_html(
                index=False,
                classes="forecast-result-table"
            ),
            unsafe_allow_html=True
        )