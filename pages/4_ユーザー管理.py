import streamlit as st
from db_service import (
    search_users,
    get_stores,
    create_user,
    deactivate_user,
    update_user_display_name,
    reset_user_password,
    update_user_store
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
# 無効化確認ダイアログ
# -----------------------

@st.dialog("ユーザー無効化の確認")
def confirm_deactivate_user(user_id, username):

    st.write(
        f"ユーザー「{username}」を無効化しますか？"
    )

    st.warning(
        "無効化すると、このユーザーはログインできなくなります。"
    )

    if st.button("無効化する"):
        success, message = deactivate_user(
            user_id,
            user.id
        )

        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

    if st.button("キャンセル"):
        st.rerun()

# -----------------------
# パスワードリセット
# -----------------------

@st.dialog("パスワードリセット")
def reset_password_dialog(user_id, display_name):

    st.write(
        f"ユーザー「{display_name}」のパスワードをリセットします。"
    )

    new_password = st.text_input(
        "新しいパスワード",
        type="password"
    )

    confirm_password = st.text_input(
        "新しいパスワード（確認）",
        type="password"
    )

    if st.button("リセットする"):

        if not new_password:
            st.error("新しいパスワードを入力してください。")

        elif not confirm_password:
            st.error("新しいパスワード（確認）を入力してください。")

        elif new_password != confirm_password:
            st.error("新しいパスワードが一致しません。")

        else:
            success, message = reset_user_password(
                user_id,
                new_password
            )

            if success:
                st.success(message)
                st.rerun()

            else:
                st.error(message)

    if st.button("キャンセル"):
        st.rerun()

# -----------------------
# ユーザー一覧
# -----------------------

st.subheader("ユーザー一覧")

keyword = st.text_input(
    "従業員番号または氏名で検索",
    placeholder="従業員番号または氏名を入力"
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
        [   "id",
            "username",
            "display_name",
            "role",
            "store_name",
            "is_active"
        ]
    ].rename(
        columns={
            "id": "内部ID",
            "username": "従業員番号",
            "display_name": "氏名",
            "role": "権限",
            "store_name": "店舗名",
            "is_active": "状態"
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

    df_users["状態"] = df_users["状態"].replace(
    {
        True: "有効",
        False: "無効"
    }
    )

    for _, row in df_users.iterrows():

        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(
            [1, 2, 2, 2, 2, 1.2, 1.2, 1.5, 2]
        )

        with col1:
            st.write(row["従業員番号"])

        with col2:
            st.write(row["氏名"])

        with col3:
            st.write(row["権限"])

        with col4:
            st.write(row["店舗名"])

        with col5:
            st.write(row["状態"])

        with col6:
            if (
                row["状態"] == "有効"
                and row["内部ID"] != user.id
            ):
                if st.button(
                    "無効化",
                    key=f"deactivate_user_{row['内部ID']}"
                ):
                    confirm_deactivate_user(
                        row["内部ID"],
                        row["氏名"]
                    )
        with col7:
            if (
                row["状態"] == "有効"
                and row["権限"] in ["一般ユーザー", "店舗責任者"]
            ):
                if st.button(
                    "店舗変更",
                    key=f"change_store_{row['内部ID']}"
                ):
                    st.session_state["change_store_user_id"] = row["内部ID"]
                    st.session_state["change_store_current"] = row["店舗名"]
        with col8:
            if row["状態"] == "有効":
                if st.button(
                    "氏名変更",
                    key=f"change_name_{row['内部ID']}"
                ):
                    st.session_state["change_name_user_id"] = row["内部ID"]
                    st.session_state["change_name_current"] = row["氏名"]
        with col9:
            if row["状態"] == "有効":
                if st.button(
                    "パスワードリセット",
                    key=f"reset_password_{row['内部ID']}"
                ):
                    reset_password_dialog(
                        row["内部ID"],
                        row["氏名"]
                    )

    if "change_store_user_id" in st.session_state:

        change_store_user_id = st.session_state["change_store_user_id"]
        current_store_name = st.session_state["change_store_current"]

        st.subheader("所属店舗変更")

        stores = get_stores()

        selected_store = st.selectbox(
            "新しい所属店舗",
            stores,
            format_func=lambda x: x.store_name
        )

        if st.button("所属店舗を変更する"):

            if selected_store.store_name == current_store_name:
                st.error("現在と同じ店舗です。")

            else:
                success, message = update_user_store(
                    change_store_user_id,
                    selected_store.id
                )

                if success:
                    st.success(message)

                    del st.session_state["change_store_user_id"]
                    del st.session_state["change_store_current"]

                    st.rerun()

                else:
                    st.error(message)
     
    if "change_name_user_id" in st.session_state:

        change_user_id = st.session_state["change_name_user_id"]
        current_name = st.session_state["change_name_current"]

        st.subheader("氏名変更")

        new_display_name = st.text_input(
            "新しい氏名",
            value=current_name
        )

        if st.button("氏名を変更する"):

            if not new_display_name.strip():
                st.error("氏名を入力してください。")

            else:
                success, message = update_user_display_name(
                    change_user_id,
                    new_display_name.strip()
                )

                if success:
                    st.success(message)

                    del st.session_state["change_name_user_id"]
                    del st.session_state["change_name_current"]

                    st.rerun()

                else:
                    st.error(message)

else:
    st.info("従業員番号または氏名を入力して検索してください。")

# -----------------------
# ユーザー追加
# -----------------------

st.subheader("ユーザー追加")

user_id = st.text_input(
    "ユーザーID（従業員番号）",
    placeholder="半角数字で入力"
)

display_name = st.text_input("氏名")

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

    if not user_id:
        st.error("従業員番号を入力してください。")

    elif not user_id.isascii() or not user_id.isdigit():
        st.error("従業員番号は半角数字で入力してください。")

    elif not display_name:
        st.error("氏名を入力してください。")

    elif not password:
        st.error("パスワードを入力してください。")

    else:
        try:

            create_user(
                user_id,
                display_name,
                password,
                role,
                store_id,
            )

            st.success("ユーザーを登録しました。")

        except ValueError as e:

            st.error(str(e))