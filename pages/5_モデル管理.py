import streamlit as st

from db_service import (
    get_system_setting,
    save_system_setting
)

from forecast_service import train_model_from_db


user = st.session_state.get("user")

if user is None:
    st.warning("ログインしてください。")
    st.stop()


# -----------------------
# 権限チェック
# -----------------------

if user.role not in ["hq_manager", "admin"]:
    st.error("このページを利用する権限がありません。")
    st.stop()

selected_store = st.session_state["selected_store"]

# -----------------------
# 人数設定
# -----------------------
st.subheader("人員配置設定")

visits_per_pharmacist = get_system_setting(
    "visits_per_pharmacist",
    25
)

new_visits_per_pharmacist = st.number_input(
    "薬剤師1人あたりの担当来局者数",
    min_value=1,
    value=visits_per_pharmacist,
    step=1
)

if st.button("設定を保存"):

    save_system_setting(
        "visits_per_pharmacist",
        new_visits_per_pharmacist
    )

    st.success("設定を保存しました。")

# -----------------------
# モデル学習
# -----------------------

st.subheader("モデル学習")

st.write(
    "選択した店舗の来局データを使用して予測モデルを学習します。"
)


if st.button("モデル学習"):

    success = train_model_from_db(
        selected_store.id
    )

    if success:
        st.success("モデル学習が完了しました。")
    else:
        st.warning(
            "学習できるデータがありません。"
        )