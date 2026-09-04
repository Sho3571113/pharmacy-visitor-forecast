from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import staffing_service


def test_save_staffing_updates_existing_staffing():
    # Arrange（準備）
    session = MagicMock()
    existing = SimpleNamespace(store_id=1, date=date(2026, 1, 1), staff_count=1)
    session.query.return_value.filter_by.return_value.first.return_value = existing

    # Act（実行）
    with patch.object(staffing_service, "Session", return_value=session):
        staffing_service.save_staffing(1, date(2026, 1, 1), 2)

    # Assert（確認）
    assert existing.staff_count == 2
    session.add.assert_not_called()
    session.commit.assert_called_once()
    session.close.assert_called_once()


def test_save_staffing_creates_new_staffing():
    # Arrange（準備）
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = None

    # Act（実行）
    with (
        patch.object(staffing_service, "Session", return_value=session),
        patch.object(staffing_service, "Staffing") as staffing,
    ):
        staffing_service.save_staffing(1, date(2026, 1, 1), 2)

    # Assert（確認）
    staffing.assert_called_once_with(
        store_id=1,
        date=date(2026, 1, 1),
        staff_count=2,
    )
    session.add.assert_called_once_with(staffing.return_value)
    session.commit.assert_called_once()
    session.close.assert_called_once()


def test_get_staffing_returns_dataframe_from_query_rows():
    # Arrange（準備）
    session = MagicMock()
    rows = [
        SimpleNamespace(store_id=1, date=date(2026, 1, 1), staff_count=2),
        SimpleNamespace(store_id=1, date=date(2026, 1, 2), staff_count=3),
    ]
    session.query.return_value.filter_by.return_value.all.return_value = rows

    # Act（実行）
    with patch.object(staffing_service, "Session", return_value=session):
        result = staffing_service.get_staffing(1)

    # Assert（確認）
    assert result.to_dict("records") == [
        {"store_id": 1, "date": date(2026, 1, 1), "staff_count": 2},
        {"store_id": 1, "date": date(2026, 1, 2), "staff_count": 3},
    ]
    session.query.assert_called_once_with(staffing_service.Staffing)
    session.query.return_value.filter_by.assert_called_once_with(store_id=1)
    session.close.assert_called_once()


def test_get_staffing_returns_empty_dataframe_when_no_data():
    # Arrange（準備）
    session = MagicMock()
    session.query.return_value.filter_by.return_value.all.return_value = []

    # Act（実行）
    with patch.object(staffing_service, "Session", return_value=session):
        result = staffing_service.get_staffing(999)

    # Assert（確認）
    assert result.empty
    session.close.assert_called_once()

def test_get_staff_suggestion_boundary_values():
    # Arrange / Act / Assert

    assert staffing_service.get_staff_suggestion(24, 25) == 1
    assert staffing_service.get_staff_suggestion(25, 25) == 1
    assert staffing_service.get_staff_suggestion(26, 25) == 2