from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///pharmacy.db"

engine = create_engine(DATABASE_URL)
