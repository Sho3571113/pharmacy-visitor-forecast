import streamlit as st
from db_service import search_users, get_stores, create_user


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
# ユーザー一覧
# -----------------------

st.subheader("ユーザー一覧")

keyword = st.text_input(
    "ユーザー名で検索",
    placeholder="ユーザー名を入力"
)

if keyword:

    df_users = search_users(keyword)

    stores = get_stores()

    store_names = {
        store.id: store.store_name
        for store in stores
    }

    df_users["store_name"] = df_users["store_id"].map(
        store_names
    )

    df_users = df_users[
        [
            "id",
            "username",
            "role",
            "store_name"
        ]
    ].rename(
        columns={
            "id": "ユーザーID",
            "username": "ユーザー名",
            "role": "権限",
            "store_name": "店舗名"
        }
    )

    df_users["権限"] = df_users["権限"].replace(
        {
            "general": "一般ユーザー",
            "store_manager": "店舗責任者",
            "hq_manager": "本部責任者",
            "admin": "システム管理者"
        }
    )

    st.markdown(
        df_users.to_html(
            index=False,
            classes="forecast-result-table"
        ),
        unsafe_allow_html=True
    )

else:
    st.info("ユーザー名を入力して検索してください。")

# -----------------------
# ユーザー追加
# -----------------------

st.subheader("ユーザー追加")

username = st.text_input("ユーザー名")


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
            username,
            password,
            role,
            store_id,
        )
        st.success("ユーザーを登録しました。")

    except ValueError as e:

        st.error(str(e))