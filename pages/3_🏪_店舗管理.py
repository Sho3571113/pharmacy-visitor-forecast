import streamlit as st
import pandas as pd
from db_service import search_stores, add_store


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





# -----------------------
# 店舗一覧
# -----------------------

st.subheader("店舗一覧")

keyword = st.text_input(
    "店舗名で検索",
    placeholder="店舗名を入力"
)

if keyword:

    stores = search_stores(keyword)

    if stores:

        df_stores = pd.DataFrame([
            {
                "店舗ID": store.id,
                "店舗名": store.store_name
            }
            for store in stores
        ])

        st.markdown(
            df_stores.to_html(
            index=False,
            classes="forecast-result-table"
            ),
        unsafe_allow_html=True
        )

    else:
        st.info("該当する店舗がありません。")

else:
    st.info("店舗名を入力して検索してください。")

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