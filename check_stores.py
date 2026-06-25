from sqlalchemy.orm import sessionmaker
from db_config import engine
from models import Store

Session = sessionmaker(bind=engine)
session = Session()

stores = session.query(Store).all()

for store in stores:
    print(store.id, store.store_name)

session.close()