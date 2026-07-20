from sqlalchemy.orm import sessionmaker
from db_config import engine
from models import User
import bcrypt


def authenticate_user(username, password):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user = session.query(User).filter_by(username=username).first()

        if user and bcrypt.checkpw(
            password.encode(),
            user.hashed_password.encode()
        ):
            return user

        return None

    finally:
        session.close()