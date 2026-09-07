from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import authentication
import pytest


def test_authenticate_user_returns_user_when_password_is_correct():
    # Arrange（準備）
    session = MagicMock()
    user = SimpleNamespace(username="test_user", hashed_password="hashed_password", is_active=True)
    session.query.return_value.filter_by.return_value.first.return_value = user
    session_factory = MagicMock(return_value=session)

    # Act（実行）
    with (
        patch.object(authentication, "sessionmaker", return_value=session_factory),
        patch.object(authentication.bcrypt, "checkpw", return_value=True) as checkpw,
    ):
        result = authentication.authenticate_user("test_user", "password")

    # Assert（確認）
    assert result == user
    session.query.assert_called_once_with(authentication.User)
    session.query.return_value.filter_by.assert_called_once_with(username="test_user")
    checkpw.assert_called_once_with(b"password", b"hashed_password")
    session.close.assert_called_once()


def test_authenticate_user_returns_none_when_user_does_not_exist():
    # Arrange（準備）
    session = MagicMock()
    session.query.return_value.filter_by.return_value.first.return_value = None
    session_factory = MagicMock(return_value=session)

    # Act（実行）
    with (
        patch.object(authentication, "sessionmaker", return_value=session_factory),
        patch.object(authentication.bcrypt, "checkpw") as checkpw,
    ):
        result = authentication.authenticate_user("unknown_user", "password")

    # Assert（確認）
    assert result is None
    session.query.return_value.filter_by.assert_called_once_with(username="unknown_user")
    checkpw.assert_not_called()
    session.close.assert_called_once()


def test_authenticate_user_returns_none_when_password_is_incorrect():
    # Arrange（準備）
    session = MagicMock()
    user = SimpleNamespace(username="test_user", hashed_password="hashed_password", is_active=True)
    session.query.return_value.filter_by.return_value.first.return_value = user
    session_factory = MagicMock(return_value=session)

    # Act（実行）
    with (
        patch.object(authentication, "sessionmaker", return_value=session_factory),
        patch.object(authentication.bcrypt, "checkpw", return_value=False) as checkpw,
    ):
        result = authentication.authenticate_user("test_user", "wrong_password")

    # Assert（確認）
    assert result is None
    checkpw.assert_called_once_with(b"wrong_password", b"hashed_password")
    session.close.assert_called_once()


def test_authenticate_user_closes_session_when_query_raises_error():
    # Arrange（準備）
    session = MagicMock()
    session.query.side_effect = RuntimeError("database error")
    session_factory = MagicMock(return_value=session)

    # Act / Assert（実行・確認）
    with patch.object(authentication, "sessionmaker", return_value=session_factory):
        with pytest.raises(RuntimeError, match="database error"):
            authentication.authenticate_user("test_user", "password")

    session.close.assert_called_once()
