import streamlit as st

from db_service import get_users, get_stores, create_user


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


st.title("👤 ユーザー管理")


# -----------------------
# ユーザー一覧
# -----------------------

st.subheader("ユーザー一覧")

df_users = get_users()

st.dataframe(
    df_users,
    use_container_width=True
)


# -----------------------
# ユーザー追加
# -----------------------

st.subheader("ユーザー追加")

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
    ]
)


# 店舗が必要な権限の場合
if role in ["general", "store_manager"]:

    stores = get_stores()

    selected_store = st.selectbox(
        "店舗",
        stores,
        format_func=lambda x: x.store_name
    )

    store_id = selected_store.id

else:

    store_id = None


# -----------------------
# ユーザー登録
# -----------------------

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