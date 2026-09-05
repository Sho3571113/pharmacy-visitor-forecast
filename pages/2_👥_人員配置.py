import streamlit as st
import pandas as pd

from db_service import (
    get_system_setting
)

from staffing_service import(
     get_staffing, 
     save_staffing, 
     get_staff_suggestion
)


user = st.session_state.get("user")

if user is None:
    st.warning("ログインしてください。")
    st.stop()

selected_store = st.session_state["selected_store"]
# -----------------------
# 推奨薬剤師人数
# -----------------------

st.subheader("推奨薬剤師人数")

df_forecast = st.session_state.get("df_forecast")

if df_forecast is None:

    st.info(
        "先に「来局者予測」画面で予測を実行してください。"
    )

else:

    df_staff = df_forecast.copy()

    # -----------------------
    # 推奨薬剤師数を計算
    # -----------------------

    visits_per_pharmacist = get_system_setting(
    "visits_per_pharmacist",
    25
)

    df_staff["推奨薬剤師数"] = (
        df_staff["predicted_visits"]
        .apply(
            lambda visits: get_staff_suggestion(
                visits,
                visits_per_pharmacist
            )
        )
    )

    # -----------------------
    # 実配置人数の初期値
    # -----------------------

    df_staff["実配置人数"] = df_staff["推奨薬剤師数"]

    # -----------------------
    # DBに保存済みの実配置人数を取得
    # -----------------------

    saved_staff = get_staffing(selected_store.id)

    if not saved_staff.empty:

        df_staff["date"] = pd.to_datetime(
            df_staff["date"]
        ).dt.date

        saved_staff["date"] = pd.to_datetime(
            saved_staff["date"]
        ).dt.date

        for _, row in saved_staff.iterrows():

            df_staff.loc[
                df_staff["date"] == row["date"],
                "実配置人数"
            ] = row["staff_count"]

    # -----------------------
    # 不足・余力を判定
    # -----------------------

    def get_staff_status(row):

        if row["実配置人数"] < row["推奨薬剤師数"]:
            shortage = (
                row["推奨薬剤師数"]
                - row["実配置人数"]
            )
            return f"{shortage}人不足"

        elif row["実配置人数"] > row["推奨薬剤師数"]:
            spare = (
                row["実配置人数"]
                - row["推奨薬剤師数"]
            )
            return f"{spare}人余力"

        else:
            return "適正"

    df_staff["状況"] = df_staff.apply(
        get_staff_status,
        axis=1
    )

    # -----------------------
    # 表示用データ
    # -----------------------

    df_display = df_staff[
        [
            "date",
            "predicted_visits",
            "推奨薬剤師数",
            "実配置人数",
            "状況"
        ]
    ].copy()

    # 日付だけ表示
    df_display["date"] = pd.to_datetime(
        df_display["date"]
    ).dt.date

    # 日本語表示
    df_display = df_display.rename(
        columns={
            "date": "日付",
            "predicted_visits": "予測来局者数"
        }
    )

    edited_df = st.data_editor(
        df_display,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------
    # 実配置人数を保存
    # -----------------------

    if st.button("実配置人数を保存"):

        for _, row in edited_df.iterrows():

            save_staffing(
                selected_store.id,
                row["日付"],
                row["実配置人数"]
            )

        st.success("実配置人数を保存しました")