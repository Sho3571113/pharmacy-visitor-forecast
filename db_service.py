from sqlalchemy.orm import sessionmaker
from db_config import engine
from models import Store, VisitData, User, ForecastResult, SystemSetting
import pandas as pd
import bcrypt

Session = sessionmaker(bind=engine)

def get_stores():
    session = Session()
    stores = session.query(Store).all()
    session.close()
    return stores

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

def create_user(
    username,
    display_name,
    password,
    role,
    store_id,
):
    session = Session()
    
    try:
        existing = (
            session.query(User)
            .filter(User.username == username)
            .first()
        )
        if existing:
            session.close()
            raise ValueError("このユーザー名は既に使用されています。")

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