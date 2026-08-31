from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

import pandas as pd
import pytest

import db_service


def test_get_stores_returns_all_stores():
    # Arrange（準備）
    session = MagicMock()
    stores = [SimpleNamespace(id=1, store_name="渋谷店")]
    session.query.return_value.all.return_value = stores

    # Act（実行）
    with patch.object(db_service, "Session", return_value=session):
        result = db_service.get_stores()

    # Assert（確認）
    assert result == stores
    session.query.assert_called_once_with(db_service.Store)
    session.close.assert_called_once()


def test_save_visit_data_saves_all_rows_and_returns_count():
    # Arrange（準備）
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "visits": [10, 20]
    })
    session = MagicMock()

    # Act（実行）
    with (
        patch.object(db_service, "Session", return_value=session),
        patch.object(db_service, "VisitData") as visit_data,
    ):
        result = db_service.save_visit_data(df, store_id=1)

    # Assert（確認）
    assert result == 2
    assert visit_data.call_args_list == [
        call(store_id=1, date=date(2026, 1, 1), visits=10),
        call(store_id=1, date=date(2026, 1, 2), visits=20),
    ]
    assert session.add.call_count == 2
    session.commit.assert_called_once()
    session.close.assert_called_once()


def test_save_visit_data_raises_error_when_required_column_is_missing():
    # Arrange（準備）
    df = pd.DataFrame({"date": ["2026-01-01"]})

    # Act / Assert（実行・確認）
    with patch.object(db_service, "Session") as session:
        with pytest.raises(ValueError, match="visits 列がありません"):
            db_service.save_visit_data(df, store_id=1)

    session.assert_not_called()


def test_get_visit_data_returns_dataframe_from_query_rows():
    # Arrange（準備）
    session = MagicMock()
    rows = [
        SimpleNamespace(store_id=1, date=date(2026, 1, 1), visits=10),
        SimpleNamespace(store_id=1, date=date(2026, 1, 2), visits=20),
    ]
    session.query.return_value.filter_by.return_value.all.return_value = rows

    # Act（実行）
    with patch.object(db_service, "Session", return_value=session):
        result = db_service.get_visit_data(store_id=1)

    # Assert（確認）
    assert result.to_dict("records") == [
        {"store_id": 1, "date": date(2026, 1, 1), "visits": 10},
        {"store_id": 1, "date": date(2026, 1, 2), "visits": 20},
    ]
    session.query.assert_called_once_with(db_service.VisitData)
    session.query.return_value.filter_by.assert_called_once_with(store_id=1)
    session.close.assert_called_once()

def test_get_visit_data_returns_empty_dataframe_when_no_data():
    # Arrange（準備）
    session = MagicMock()
    session.query.return_value.filter_by.return_value.all.return_value = []

    # Act（実行）
    with patch.object(db_service, "Session", return_value=session):
        result = db_service.get_visit_data(store_id=999)

    # Assert（確認）
    assert result.empty
    session.query.assert_called_once_with(db_service.VisitData)
    session.query.return_value.filter_by.assert_called_once_with(store_id=999)
    session.close.assert_called_once()


def test_save_visit_data_returns_zero_when_dataframe_is_empty():
    # Arrange（準備）
    df = pd.DataFrame(columns=["date", "visits"])
    session = MagicMock()

    # Act（実行）
    with (
        patch.object(db_service, "Session", return_value=session),
        patch.object(db_service, "VisitData"),
    ):
        result = db_service.save_visit_data(df, store_id=1)

    # Assert（確認）
    assert result == 0
    session.add.assert_not_called()
    session.commit.assert_called_once()
    session.close.assert_called_once()


def test_save_visit_data_accepts_timestamp():
    # Arrange（準備）
    df = pd.DataFrame({
        "date": [pd.Timestamp("2026-01-01")],
        "visits": [10]
    })
    session = MagicMock()

    # Act（実行）
    with (
        patch.object(db_service, "Session", return_value=session),
        patch.object(db_service, "VisitData") as visit_data,
    ):
        result = db_service.save_visit_data(df, store_id=1)

    # Assert（確認）
    assert result == 1
    visit_data.assert_called_once_with(
        store_id=1,
        date=date(2026, 1, 1),
        visits=10,
    )
    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.close.assert_called_once()

def test_add_store_adds_new_store():
    # Arrange
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = None

    # Act
    with patch.object(db_service, "Session", return_value=session):
        result = db_service.add_store("横浜店")

    # Assert
    assert result is True

    session.query.assert_called_once_with(db_service.Store)
    session.query.return_value.filter_by.assert_called_once_with(
        store_name="横浜店"
    )

    session.add.assert_called_once()
    added_store = session.add.call_args.args[0]

    assert isinstance(added_store, db_service.Store)
    assert added_store.store_name == "横浜店"

    session.commit.assert_called_once()
    session.close.assert_called_once()

def test_add_store_does_not_add_existing_store():
    # Arrange
    session = MagicMock()

    existing_store = SimpleNamespace(
        id=4,
        store_name="横浜店"
    )

    session.query.return_value.filter_by.return_value.first.return_value = existing_store

    # Act
    with patch.object(db_service, "Session", return_value=session):
        result = db_service.add_store("横浜店")

    # Assert
    assert result is False
    session.query.assert_called_once_with(db_service.Store)
    session.query.return_value.filter_by.assert_called_once_with(
        store_name="横浜店"
    )
    session.add.assert_not_called()
    session.commit.assert_not_called()
    session.close.assert_called_once()