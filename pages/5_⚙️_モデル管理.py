import streamlit as st

from db_service import get_stores
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


st.title("⚙️ モデル管理")


# -----------------------
# 店舗選択
# -----------------------

st.subheader("店舗選択")

stores = get_stores()

selected_store = st.selectbox(
    "店舗",
    stores,
    format_func=lambda x: x.store_name
)


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