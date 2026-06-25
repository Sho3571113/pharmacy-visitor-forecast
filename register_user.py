from sqlalchemy.orm import sessionmaker
from db_config import engine
from models import User
import bcrypt

def register_user(username, display_name, password, role="general"):
    Session = sessionmaker(bind=engine)
    session = Session()

    if session.query(User).filter_by(username=username).first():
        return False, "このユーザー名は既に存在します"

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    user = User(
        username=username,
        display_name=display_name,
        hashed_password=hashed_pw,
        role=role
    )

    session.add(user)
    session.commit()
    return True, "ユーザー登録が完了しました"
