from sqlalchemy.orm import sessionmaker
from db_config import engine
from models import Store, VisitData
import pandas as pd

Session = sessionmaker(bind=engine)

def get_stores():
    session = Session()
    stores = session.query(Store).all()
    session.close()
    return stores


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