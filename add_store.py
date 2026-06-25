from sqlalchemy.orm import sessionmaker
from db_config import engine
from models import Store

Session = sessionmaker(bind=engine)
session = Session()

stores = [
    "新宿店",
    "渋谷店",
    "池袋店"
]

for name in stores:

    existing = session.query(Store).filter_by(
        store_name=name
    ).first()

    if not existing:
        session.add(
            Store(store_name=name)
        )

session.commit()
session.close()

print("店舗登録完了")