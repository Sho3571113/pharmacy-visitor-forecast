import streamlit as st

from db_service import get_stores, add_store


user = st.session_state.get("user")

if user is None:
    st.warning("ログインしてください。")
    st.stop()


# -----------------------
# 権限チェック
# -----------------------

if user.role != "admin":
    st.error("このページを利用する権限がありません。")
    st.stop()


st.title("🏪 店舗管理")


# -----------------------
# 店舗一覧
# -----------------------

st.subheader("店舗一覧")

stores = get_stores()

for store in stores:
    st.write(
        f"店舗ID: {store.id}　店舗名: {store.store_name}"
    )


# -----------------------
# 店舗追加
# -----------------------

st.subheader("店舗追加")

store_name = st.text_input("店舗名")


if st.button("店舗追加"):

    if not store_name:

        st.error("店舗名を入力してください")

    else:

        result = add_store(store_name)

        if result:

            st.success("店舗を追加しました")
            st.rerun()

        else:

            st.warning("その店舗は既に存在します")