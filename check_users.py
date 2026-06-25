from sqlalchemy.orm import sessionmaker
from db_config import engine
from models import User

Session = sessionmaker(bind=engine)
session = Session()

users = session.query(User).all()

for user in users:
    print(
        user.id,
        user.username,
        user.display_name,
        user.role
    )