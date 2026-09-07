import streamlit as st
import pandas as pd
from db_service import (
     search_stores, 
     add_store,
     update_store_name,
     deactivate_store,

)

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
# 店舗無効化確認ダイアログ
# -----------------------

@st.dialog("店舗無効化の確認")
def confirm_deactivate_store(store_id, store_name):

    st.write(
        f"店舗「{store_name}」を無効化しますか？"
    )

    st.warning(
        "無効化すると、この店舗は新規の店舗選択対象から外れます。"
    )

    if st.button("無効化する"):

        success, message = deactivate_store(
            store_id
        )

        if success:
            st.success(message)
            st.rerun()

        else:
            st.error(message)

    if st.button("キャンセル"):
        st.rerun()

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
                "店舗名": store.store_name,
               "状態": "有効" if store.is_active else "無効"
            }
            for store in stores
        ])

        for _, row in df_stores.iterrows():

            col1, col2, col3, col4, col5 = st.columns([1, 3, 1.2, 1.5, 1.5])

            with col1:
                st.write(row["店舗ID"])

            with col2:
                st.write(row["店舗名"])

            with col3:
                st.write(row["状態"])

            with col4:
                if row["状態"] == "有効":
                    if st.button(
                        "店舗名変更",
                        key=f"change_store_name_{row['店舗ID']}"
                    ):
                        st.session_state["change_store_id"] = row["店舗ID"]
                        st.session_state["change_store_current"] = row["店舗名"]

            with col5:
                if row["状態"] == "有効":
                    if st.button(
                        "店舗無効化",
                        key=f"deactivate_store_{row['店舗ID']}"
                    ):
                        confirm_deactivate_store(
                            row["店舗ID"],
                            row["店舗名"]
                        )
            
    else:
        st.info("該当する店舗がありません。")

else:
    st.info("店舗名を入力して検索してください。")

# -----------------------
# 店舗名変更
# -----------------------

if "change_store_id" in st.session_state:

    change_store_id = st.session_state["change_store_id"]
    current_store_name = st.session_state["change_store_current"]

    st.subheader("店舗名変更")

    new_store_name = st.text_input(
        "新しい店舗名",
        value=current_store_name
    )

    if st.button("店舗名を変更する"):

        if not new_store_name.strip():
            st.error("店舗名を入力してください。")

        else:
            success, message = update_store_name(
                change_store_id,
                new_store_name.strip()
            )

            if success:
                st.success(message)

                del st.session_state["change_store_id"]
                del st.session_state["change_store_current"]

                st.rerun()

            else:
                st.error(message)


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