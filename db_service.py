from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_
from db_config import engine
from models import Store, VisitData, User, ForecastResult, Staffing, SystemSetting
import pandas as pd
import bcrypt

Session = sessionmaker(bind=engine)

def get_stores():
    session = Session()
    stores = (
        session.query(Store)
        .filter(Store.is_active == True)
        .all()
    )
    session.close()
    return stores

def search_stores(keyword=""):
    session = Session()

    try:
        query = session.query(Store)

        if keyword:
            query = query.filter(
                Store.store_name.contains(keyword)
            )

        rows = (
            query
            .order_by(Store.id)
            .all()
        )

        return rows

    finally:
        session.close()

def get_users():
    session = Session()

    rows = session.query(User).all()

    session.close()

    df = pd.DataFrame([
        {
            "id": row.id,
            "username": row.username,
            "display_name": row.display_name,
            "role": row.role,
            "store_id": row.store_id,
            "created_at": row.created_at,
        }
        for row in rows
    ])

    return df

def search_users(keyword="", limit=50):
    session = Session()

    try:
        query = session.query(User)

        if keyword:
            query = query.filter(
                or_(
                    User.username.contains(keyword),
                    User.display_name.contains(keyword)
                )
            )

        rows = (
            query
            .order_by(User.id)
            .limit(limit)
            .all()
        )

        df = pd.DataFrame([
            {
                "id": row.id,
                "username": row.username,
                "display_name": row.display_name,
                "role": row.role,
                "store_id": row.store_id,
                "is_active": row.is_active,
                "created_at": row.created_at,
            }
            for row in rows
        ])

        return df

    finally:
        session.close()

def create_user(
    username,
    display_name,
    password,
    role,
    store_id,
):
    session = Session()
    
    try:

        if not username:
            raise ValueError("従業員番号を入力してください。")

        if not username.isascii() or not username.isalnum():
            raise ValueError(
                "従業員番号は半角英数字で入力してください。"
            )

        if not display_name.strip():
            raise ValueError("氏名を入力してください。")

        if not password:
            raise ValueError("パスワードを入力してください。")

        if any(char.isspace() for char in password):
            raise ValueError("パスワードに空白は使用できません。")

        existing = (
            session.query(User)
            .filter(User.username == username)
            .first()
        )

        if existing:
            raise ValueError(
                "この従業員番号は既に使用されています。"
            )

        hashed_password = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

        user = User(
            username=username,
            display_name=display_name,
            hashed_password=hashed_password,
            role=role,
            store_id=store_id,
        )

        session.add(user)
        session.commit()
    
    finally:
        session.close()

def update_user_store(user_id, store_id):

    session = Session()

    try:
        user = (
            session.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            return False, "ユーザーが見つかりません。"

        if not user.is_active:
            return False, "無効なユーザーの所属店舗は変更できません。"

        if user.role not in ["general", "store_manager"]:
            return False, "この権限のユーザーは所属店舗を変更できません。"

        store = (
            session.query(Store)
            .filter(Store.id == store_id)
            .first()
        )

        if store is None:
            return False, "店舗が見つかりません。"

        if not store.is_active:
            return False, "無効な店舗には変更できません。"

        user.store_id = store_id

        session.commit()

        return True, "所属店舗を変更しました。"

    finally:
        session.close()

def deactivate_user(user_id, current_user_id):

    session = Session()

    try:
        if user_id == current_user_id:
            return False, "自分自身は無効化できません。"

        user = (
            session.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            return False, "ユーザーが見つかりません。"

        if not user.is_active:
            return False, "このユーザーは既に無効です。"

        if user.role == "admin":

            admin_count = (
                session.query(User)
                .filter(
                    User.role == "admin",
                    User.is_active == True
                )
                .count()
            )

            if admin_count <= 1:
                return False, "adminが1人しかいないため、無効化できません。"

        user.is_active = False

        session.commit()

        return True, "ユーザーを無効化しました。"

    finally:
        session.close()

def update_user_display_name(user_id, display_name):

    session = Session()

    try:
        user = (
            session.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            return False, "ユーザーが見つかりません。"

        if not user.is_active:
            return False, "無効なユーザーの氏名は変更できません。"

        if not display_name.strip():
            return False, "氏名を入力してください。"

        user.display_name = display_name.strip()

        session.commit()

        return True, "氏名を変更しました。"

    finally:
        session.close()

def reset_user_password(user_id, new_password):

    session = Session()

    try:
        user = (
            session.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            return False, "ユーザーが見つかりません。"

        if not user.is_active:
            return False, "無効なユーザーのパスワードは変更できません。"

        if not new_password.strip():
            return False, "新しいパスワードを入力してください。"

        if any(char.isspace() for char in new_password):
            return False, "パスワードに空白は使用できません。"
        hashed_password = bcrypt.hashpw(
            new_password.encode(),
            bcrypt.gensalt()
        ).decode()

        user.hashed_password = hashed_password

        session.commit()

        return True, "パスワードをリセットしました。"

    finally:
        session.close()

def has_visit_data():
    session = Session()

    try:
        return session.query(VisitData).first() is not None

    finally:
        session.close()

def save_visit_data(df, store_id):
        
        required_columns = ["date", "visits"]

        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"{col} 列がありません")
                
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        

        session = Session()

        saved_count = 0

        for _, row in df.iterrows():

            visit_date = pd.to_datetime(row["date"]).date()

            visit = VisitData(
                store_id=store_id,
                date=visit_date,
                visits=row["visits"]
            )

            session.add(visit)
            saved_count += 1

        session.commit()
        session.close()

        return saved_count


def get_visit_data(store_id):

    session = Session()

    rows = session.query(
        VisitData
    ).filter_by(
        store_id=store_id
    ).all()

    session.close()

    df = pd.DataFrame([
        {
            "store_id": row.store_id,
            "date": row.date,
            "visits": row.visits
        }
        for row in rows
    ])

    return df

def save_forecast_result(store_id, date, predicted_visits):

    session = Session()

    try:
        forecast = (
            session.query(ForecastResult)
            .filter(
                ForecastResult.store_id == store_id,
                ForecastResult.date == date
            )
            .first()
        )

        if forecast:
            forecast.predicted_visits = predicted_visits

        else:
            forecast = ForecastResult(
                store_id=store_id,
                date=date,
                predicted_visits=predicted_visits
            )

            session.add(forecast)

        session.commit()

    finally:
        session.close()

def get_forecast_result(store_id):

    session = Session()

    try:
        rows = (
            session.query(ForecastResult)
            .filter(ForecastResult.store_id == store_id)
            .order_by(ForecastResult.date)
            .all()
        )

        df = pd.DataFrame([
            {
                "date": row.date,
                "predicted_visits": row.predicted_visits
            }
            for row in rows
        ])

        return df

    finally:
        session.close()

def add_store(store_name):

    session = Session()

    try:
        existing = (
            session.query(Store)
            .filter_by(store_name=store_name)
            .first()
        )

        if existing:
            return False

        session.add(
            Store(store_name=store_name)
        )

        session.commit()
        return True

    finally:
        session.close()

def update_store_name(store_id, store_name):
    session = Session()

    try:
        store = (
            session.query(Store)
            .filter(Store.id == store_id)
            .first()
        )

        if store is None:
            return False, "店舗が見つかりません。"

        if not store.is_active:
            return False, "無効な店舗の名称は変更できません。"

        if not store_name.strip():
            return False, "店舗名を入力してください。"

        existing = (
            session.query(Store)
            .filter(
                Store.store_name == store_name.strip(),
                Store.id != store_id
            )
            .first()
        )

        if existing:
            return False, "その店舗名は既に使用されています。"

        store.store_name = store_name.strip()

        session.commit()

        return True, "店舗名を変更しました。"

    finally:
        session.close()

def deactivate_store(store_id):

    session = Session()

    try:
        store = (
            session.query(Store)
            .filter(Store.id == store_id)
            .first()
        )

        if store is None:
            return False, "店舗が見つかりません。"

        if not store.is_active:
            return False, "この店舗は既に無効です。"

        has_active_users = (
            session.query(User)
            .filter(
                User.store_id == store_id,
                User.is_active == True
            )
            .first()
            is not None
        )

        if has_active_users:
            return False, "有効なユーザーが所属しているため、店舗を無効化できません。"

        store.is_active = False
        session.commit()

        return True, "店舗を無効化しました。"

    finally:
        session.close()


def save_system_setting(setting_name, setting_value):
    with Session() as session:

        setting = session.query(SystemSetting).filter_by(
            setting_name=setting_name
        ).first()

        if setting:
            setting.setting_value = setting_value

        else:
            setting = SystemSetting(
                setting_name=setting_name,
                setting_value=setting_value
            )

            session.add(setting)

        session.commit()

def get_system_setting(setting_name, default=None):
    with Session() as session:

        setting = session.query(SystemSetting).filter_by(
            setting_name=setting_name
        ).first()

        if setting:
            return setting.setting_value

        return default