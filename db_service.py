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
    
        session = Session()

        saved_count = 0

        for _, row in df.iterrows():

            visit_date = pd.to_datetime(row["date"]).date()

            existing = session.query(
                        VisitData
            ).filter_by(
                store_id=store_id,
                date=visit_date
            ).first()

            if existing:
                continue

            visit = VisitData(
                store_id=store_id,
                date=visit_date,
                visits=int(row["visits"])
            )

            session.add(visit)
            saved_count += 1

        session.commit()
        session.close()

        return saved_count