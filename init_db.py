from sqlalchemy.orm import sessionmaker
from db_config import engine
from models import Base, User, Store
import bcrypt


# テーブル作成
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

try:
    # 初期管理者が存在するか確認
    admin = (
        session.query(User)
        .filter(User.username == "admin")
        .first()
    )

    if admin is None:
        hashed_password = bcrypt.hashpw(
            "admin123".encode(),
            bcrypt.gensalt()
        ).decode()

        admin = User(
            username="admin",
            display_name="初期管理者",
            hashed_password=hashed_password,
            role="admin",
            is_active=True
        )

        session.add(admin)
        session.commit()

        print("初期管理者を作成しました。")
        print("ユーザー名: admin")
        print("パスワード: admin123")

    else:
        print("adminユーザーは既に存在します。")

    # 初期店舗が存在するか確認
    store = (
        session.query(Store)
        .filter(Store.store_name == "サンプル店舗")
        .first()
    )

    if store is None:
        store = Store(
            store_name="サンプル店舗",
            is_active=True
        )

        session.add(store)
        session.commit()

        print("サンプル店舗を作成しました。")
    else:
        print("サンプル店舗は既に存在します。")   

finally:
    session.close()