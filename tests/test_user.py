import db_service
import pytest
from db_service import create_user
from models import Base, Store, User

# ユーザーを正常に作成できる
def test_create_user_success(test_session):

    create_user(
        username="10001",
        display_name="テストユーザー",
        password="password123",
        role="general",
        store_id=None
    )

    session = test_session()

    user = (
        session.query(User)
        .filter(User.username == "10001")
        .first()
    )

    assert user is not None
    assert user.display_name == "テストユーザー"
    assert user.role == "general"
    assert user.is_active is True

    # パスワードそのものではなく、ハッシュ化されていることを確認
    assert user.hashed_password != "password123"

    session.close()

# 重複した従業員番号ではユーザーを作成できない
def test_create_user_duplicate_username(test_session):

    create_user(
        username="10002",
        display_name="最初のユーザー",
        password="password123",
        role="general",
        store_id=None
    )

    try:
        create_user(
            username="10002",
            display_name="重複ユーザー",
            password="password456",
            role="general",
            store_id=None
        )
        assert False, "重複した従業員番号なのにユーザーを作成できました。"

    except ValueError as e:
        assert str(e) == "この従業員番号は既に使用されています。"

# 従業員番号が数字以外の場合はユーザーを作成できない
def test_create_user_invalid_username(test_session):

    try:
        create_user(
            username="abc123",
            display_name="テストユーザー",
            password="password123",
            role="general",
            store_id=None
        )
        assert False, "数字以外の従業員番号なのにユーザーを作成できました。"

    except ValueError as e:
        assert str(e) == "従業員番号は半角数字で入力してください。"

# ユーザーを正常に無効化できる
def test_deactivate_user_success(test_session):
    from db_service import deactivate_user

    session = test_session()

    user = User(
        username="10004",
        display_name="無効化テストユーザー",
        hashed_password="dummy",
        role="general",
        is_active=True,
        store_id=None
    )

    admin = User(
        username="90001",
        display_name="管理者",
        hashed_password="dummy",
        role="admin",
        is_active=True,
        store_id=None
    )

    session.add_all([user, admin])
    session.commit()

    success, message = deactivate_user(user.id, admin.id)

    assert success is True
    assert message == "ユーザーを無効化しました。"

    session.refresh(user)
    assert user.is_active is False

    session.close()

# 自分自身は無効化できない
def test_deactivate_user_self(test_session):
    from db_service import deactivate_user

    session = test_session()

    user = User(
        username="10005",
        display_name="本人",
        hashed_password="dummy",
        role="general",
        is_active=True,
        store_id=None
    )

    session.add(user)
    session.commit()

    success, message = deactivate_user(user.id, user.id)

    assert success is False
    assert message == "自分自身は無効化できません。"

    session.refresh(user)
    assert user.is_active is True

    session.close()

# 最後の1人の管理者は無効化できない
def test_deactivate_last_admin(test_session):
    from db_service import deactivate_user

    session = test_session()

    admin = User(
        username="90002",
        display_name="唯一の管理者",
        hashed_password="dummy",
        role="admin",
        is_active=True,
        store_id=None
    )

    session.add(admin)
    session.commit()

    success, message = deactivate_user(admin.id, 99999)

    assert success is False
    assert message == "adminが1人しかいないため、無効化できません。"

    session.refresh(admin)
    assert admin.is_active is True

    session.close()

# 無効なユーザーは無効化できない
def test_deactivate_inactive_user(test_session):
    from db_service import deactivate_user

    session = test_session()

    user = User(
        username="10006",
        display_name="既に無効なユーザー",
        hashed_password="dummy",
        role="general",
        is_active=False,
        store_id=None
    )

    admin = User(
        username="90003",
        display_name="管理者",
        hashed_password="dummy",
        role="admin",
        is_active=True,
        store_id=None
    )

    session.add_all([user, admin])
    session.commit()

    success, message = deactivate_user(user.id, admin.id)

    assert success is False
    assert message == "このユーザーは既に無効です。"

    session.refresh(user)
    assert user.is_active is False

    session.close()

# ユーザーのパスワードを正常にリセットできる
def test_reset_user_password_success(test_session):
    from db_service import reset_user_password
    import bcrypt

    session = test_session()

    user = User(
        username="10007",
        display_name="パスワードテストユーザー",
        hashed_password=bcrypt.hashpw(
            b"oldpassword",
            bcrypt.gensalt()
        ).decode(),
        role="general",
        is_active=True,
        store_id=None
    )

    session.add(user)
    session.commit()

    success, message = reset_user_password(
        user.id,
        "newpassword123"
    )

    assert success is True
    assert message == "パスワードをリセットしました。"

    session.refresh(user)

    # 新しいパスワードで認証できる
    assert bcrypt.checkpw(
        b"newpassword123",
        user.hashed_password.encode()
    )

    # 古いパスワードでは認証できない
    assert not bcrypt.checkpw(
        b"oldpassword",
        user.hashed_password.encode()
    )

    session.close()

# 無効なユーザーのパスワードはリセットできない
def test_reset_password_inactive_user(test_session):
    from db_service import reset_user_password

    session = test_session()

    user = User(
        username="10008",
        display_name="無効ユーザー",
        hashed_password="dummy",
        role="general",
        is_active=False,
        store_id=None
    )

    session.add(user)
    session.commit()

    success, message = reset_user_password(
        user.id,
        "newpassword123"
    )

    assert success is False
    assert message == "無効なユーザーのパスワードは変更できません。"

    session.refresh(user)
    assert user.is_active is False

    session.close()