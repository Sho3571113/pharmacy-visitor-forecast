from sqlalchemy.orm import sessionmaker
from db_config import engine
from models import Staffing
import pandas as pd


Session = sessionmaker(bind=engine)

def save_staffing(store_id, date, staff_count):

    session = Session()

    existing = session.query(
        Staffing
    ).filter_by(
        store_id=store_id,
        date=date
    ).first()
    if existing:
        existing.staff_count = staff_count
    else:
        staffing = Staffing(
            store_id=store_id,
            date=date,
            staff_count=staff_count
        )

        session.add(staffing)

    session.commit()

    session.close()

def get_staffing(store_id):

    session = Session()

    rows = session.query(
        Staffing
    ).filter_by(
        store_id=store_id
    ).all()

    session.close()

    df = pd.DataFrame([
        {
            "store_id": row.store_id,
            "date": row.date,
            "staff_count": row.staff_count
        }
        for row in rows
    ])

    return df