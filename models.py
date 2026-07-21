from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Float
from datetime import datetime


Base = declarative_base()


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    store_name = Column(String, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)

    role = Column(String, default="general")

    store_id = Column(Integer, ForeignKey("stores.id"))

    created_at = Column(DateTime, default=datetime.utcnow)


class VisitData(Base):
    __tablename__ = "visit_data"

    id = Column(Integer, primary_key=True)

    store_id = Column(Integer, ForeignKey("stores.id"))

    date = Column(Date, nullable=False)

    visits = Column(Integer, nullable=False)

class Staffing(Base):
    __tablename__ = "staffing"

    id = Column(Integer, primary_key=True)

    store_id = Column(
        Integer,
        ForeignKey("stores.id"),
        nullable=False
    )

    date = Column(Date, nullable=False)

    staff_count = Column(Integer, nullable=False)

class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id = Column(Integer, primary_key=True)

    store_id = Column(
        Integer,
        ForeignKey("stores.id"),
        nullable=False
    )

    date = Column(Date, nullable=False)

    predicted_visits = Column(
        Float,
        nullable=False
    )