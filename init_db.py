from sqlalchemy.orm import sessionmaker
from db_config import engine
from models import Base, User, Store
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

initial_username = os.getenv("INITIAL_ADMIN_USERNAME")
initial_password = os.getenv("INITIAL_ADMIN_PASSWORD")

if not initial_username or not initial_password:
    raise ValueError(
        "INITIAL_ADMIN_USERNAME と INITIAL_ADMIN_PASSWORD を設定してください。"
    )

# テーブル作成
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

try:
    # 初期管理者が存在するか確認
    admin = (
        session.query(User)
        .filter(User.username == initial_username)
        .first()
)

    if admin is None:
        hashed_password = bcrypt.hashpw(
            initial_password.encode(),
            bcrypt.gensalt()
        ).decode() 

        admin = User(
            username=initial_username,
            display_name="初期管理者",
            hashed_password=hashed_password,
            role="admin",
            is_active=True
        )

        session.add(admin)
        session.commit()

        print("初期管理者を作成しました。")

    else:
        print("初期管理者は既に存在します。")

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