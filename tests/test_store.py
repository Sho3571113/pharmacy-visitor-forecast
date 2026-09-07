import db_service
from db_service import deactivate_store
from models import Store, User

#ユーザーがいる店舗は無効化できない
def test_deactivate_store_with_active_user(test_session):

    session = test_session()

    store = Store(
        store_name="テスト店舗",
        is_active=True
    )

    session.add(store)
    session.commit()

    user = User(
        username="10001",
        display_name="テストユーザー",
        hashed_password="dummy",
        role="general",
        is_active=True,
        store_id=store.id
    )

    session.add(user)
    session.commit()

    success, message = deactivate_store(store.id)

    assert success is False
    assert message == "有効なユーザーが所属しているため、店舗を無効化できません。"

    session.close()

# 無効ユーザーしかいない店舗は無効化できる
def test_deactivate_store_with_inactive_user(test_session):

    session = test_session()

    store = Store(
        store_name="無効ユーザーテスト店舗",
        is_active=True
    )

    session.add(store)
    session.commit()

    user = User(
        username="10002",
        display_name="無効ユーザー",
        hashed_password="dummy",
        role="general",
        is_active=False,
        store_id=store.id
    )

    session.add(user)
    session.commit()

    success, message = deactivate_store(store.id)

    assert success is True
    assert message == "店舗を無効化しました。"

    session.close()

# ユーザーがいない店舗は無効化できる
def test_deactivate_store_without_users(test_session):

    session = test_session()

    store = Store(
        store_name="ユーザーなしテスト店舗",
        is_active=True
    )

    session.add(store)
    session.commit()

    success, message = deactivate_store(store.id)

    assert success is True
    assert message == "店舗を無効化しました。"

    session.close()