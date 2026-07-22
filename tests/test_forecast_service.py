from unittest.mock import MagicMock, call, patch

import pandas as pd

import forecast_service


def test_forecast_from_db_returns_none_when_visit_data_is_empty():
    # Arrange（準備）
    empty_df = pd.DataFrame()

    # Act（実行）
    with patch.object(forecast_service, "get_visit_data", return_value=empty_df):
        result, model = forecast_service.forecast_from_db(1, 7)

    # Assert（確認）
    assert result is None
    assert model is None


def test_forecast_from_db_returns_none_when_saved_model_does_not_exist():
    # Arrange（準備）
    df_db = pd.DataFrame({
        "date": ["2026-01-01"],
        "visits": [10]
    })

    # Act（実行）
    with (
        patch.object(forecast_service, "get_visit_data", return_value=df_db),
        patch.object(forecast_service.joblib, "load", side_effect=FileNotFoundError),
    ):
        result, model = forecast_service.forecast_from_db(1, 7)

    # Assert（確認）
    assert result is None
    assert model is None


def test_forecast_from_db_saves_each_forecast_result():
    # Arrange（準備）
    df_db = pd.DataFrame({
        "date": ["2026-01-02", "2026-01-01"],
        "visits": [20, 10]
    })
    df_forecast = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-03", "2026-01-04"]),
        "predicted_visits": [30, 40]
    })
    model = MagicMock()
    le = MagicMock()

    # Act（実行）
    with (
        patch.object(forecast_service, "get_visit_data", return_value=df_db),
        patch.object(forecast_service.joblib, "load", side_effect=[model, le]),
        patch.object(forecast_service, "forecast_visits", return_value=df_forecast) as forecast_visits,
        patch.object(forecast_service, "save_forecast_result") as save_forecast_result,
    ):
        result, returned_model = forecast_service.forecast_from_db(1, 2)

    # Assert（確認）
    assert result.equals(df_forecast)
    assert returned_model == model
    forecast_args = forecast_visits.call_args.args
    assert list(forecast_args[2]["date"]) == [pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-02")]
    assert forecast_args[3] == pd.Timestamp("2026-01-02")
    assert forecast_args[4] == 2
    assert save_forecast_result.call_args_list == [
        call(1, pd.Timestamp("2026-01-03"), 30),
        call(1, pd.Timestamp("2026-01-04"), 40),
    ]


def test_forecast_from_db_returns_model_when_forecast_fails():
    # Arrange（準備）
    df_db = pd.DataFrame({
        "date": ["2026-01-01"],
        "visits": [10]
    })
    model = MagicMock()
    le = MagicMock()

    # Act（実行）
    with (
        patch.object(forecast_service, "get_visit_data", return_value=df_db),
        patch.object(forecast_service.joblib, "load", side_effect=[model, le]),
        patch.object(forecast_service, "forecast_visits", return_value=None),
        patch.object(forecast_service, "save_forecast_result") as save_forecast_result,
    ):
        result, returned_model = forecast_service.forecast_from_db(1, 7)

    # Assert（確認）
    assert result is None
    assert returned_model == model
    save_forecast_result.assert_not_called()


def test_train_model_from_db_returns_false_when_visit_data_is_empty():
    # Arrange（準備）
    empty_df = pd.DataFrame()

    # Act（実行）
    with patch.object(forecast_service, "get_visit_data", return_value=empty_df):
        result = forecast_service.train_model_from_db(1)

    # Assert（確認）
    assert result is False


def test_train_model_from_db_trains_and_saves_model():
    # Arrange（準備）
    df_db = pd.DataFrame({
        "date": ["2026-01-02", "2026-01-01"],
        "visits": [20, 10]
    })
    model = MagicMock()
    le = MagicMock()

    # Act（実行）
    with (
        patch.object(forecast_service, "get_visit_data", return_value=df_db),
        patch.object(forecast_service, "train_lightgbm_model", return_value=(model, le)) as train_model,
        patch.object(forecast_service.joblib, "dump") as dump,
    ):
        result = forecast_service.train_model_from_db(1)

    # Assert（確認）
    assert result is True
    trained_df = train_model.call_args.args[0]
    assert list(trained_df["date"]) == [pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-02")]
    assert dump.call_args_list == [
        call(model, forecast_service.MODEL_PATH),
        call(le, forecast_service.LABEL_ENCODER_PATH),
    ]
