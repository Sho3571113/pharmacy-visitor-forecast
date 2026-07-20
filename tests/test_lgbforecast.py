#正しくデータ列ができているか#
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from lgbforecast import create_features, forecast_visits

def test_create_features_adds_day_column():
     # Arrange（準備）
    df = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"]),
        "visits": [10, 20, 30]
    })
# Act（実行）
    result = create_features(df)

# Assert（確認）
    assert "day" in result.columns
    
    assert result["day"].iloc[0] == 1
    assert result["day"].iloc[1] == 2
    
    assert pd.isna(result["lag1"].iloc[0])
    assert result["lag1"].iloc[1] == 10

    assert result["rolling7"].iloc[2] == 15

#正常系でモデルが正しく作られているか#
from lgbforecast import train_lightgbm_model
def test_train_lightgbm_model_returns_model():
    df = pd.DataFrame({
        "date": pd.date_range(
            start="2026-01-01",
            periods=31,
            freq="D"
        ),
        "visits": range(30, 61)
    })

    model, _ = train_lightgbm_model(df)

    assert model is not None

#異常系、エラーが出るか#
import pytest
def test_train_lightgbm_model_raises_error_when_data_too_small():
    df = pd.DataFrame({
        "date": pd.date_range(
            start="2026-01-01",
            periods=10,
            freq="D"
        ),
        "visits": range(30, 40)
    })
    with pytest.raises(ValueError):
        train_lightgbm_model(df)

#境界値#
import pytest
def test_train_lightgbm_model_raises_error_with_29_rows():
    df = pd.DataFrame({
        "date": pd.date_range(
            start="2026-01-01",
            periods=29,
            freq="D"
        ),
        "visits": range(30, 59)
    })
    with pytest.raises(ValueError):
        train_lightgbm_model(df)

def test_train_lightgbm_model_accepts_30_rows():
    df = pd.DataFrame({
        "date": pd.date_range(
            start="2026-01-01",
            periods=30,
            freq="D"
        ),
        "visits": range(30, 60)
    })
    
    model, _ = train_lightgbm_model(df)

    assert model is not None 

#weather列有無
def test_train_lightgbm_model_weather_none():
    df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=30),
        "visits": range(30, 60)
        })

    model, le = train_lightgbm_model(df)

    assert model is not None
    assert le is None

def test_train_lightgbm_model_weather_exists():
    df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=30),
        "visits": range(30, 60),
        "weather": [
            "晴", "曇", "雨"
        ] * 10
    })
    model, le = train_lightgbm_model(df)

    assert model is not None
    assert le is not None
    assert set(le.classes_) == {"晴", "曇", "雨"}

#予測結果を日数分返すか。正常、境界
def test_forecast_visits_1day():
    df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=30),
        "visits": range(30, 60),
        "weather": [
            "晴", "曇", "雨"
        ] * 10
    })
    model, le = train_lightgbm_model(df)
    last_date = df["date"].max()

    result = forecast_visits(
    model,
    le,
    df,
    last_date,
    1
    )

    assert len(result) == 1
    assert "date" in result.columns
    assert "predicted_visits" in result.columns
    assert result["date"].iloc[0] == last_date + pd.Timedelta(days=1)


class RecordingModel:
    def __init__(self):
        self.features = []

    def predict(self, feature):
        self.features.append(feature.copy())
        return [100]


def test_forecast_visits_uses_weather_list():
    # Arrange（準備）
    history_df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=3),
        "visits": [10, 20, 30]
    })
    model = RecordingModel()
    le = LabelEncoder().fit(["晴", "曇", "雨"])
    weather_list = ["晴", "雨"]

    # Act（実行）
    result = forecast_visits(
        model, le, history_df, history_df["date"].max(), 2, weather_list=weather_list
    )

    # Assert（確認）
    assert len(result) == 2
    assert model.features[0]["weather_encoded"].iloc[0] == le.transform(["晴"])[0]
    assert model.features[1]["weather_encoded"].iloc[0] == le.transform(["雨"])[0]


def test_forecast_visits_uses_temp_list():
    # Arrange（準備）
    history_df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=3),
        "visits": [10, 20, 30]
    })
    model = RecordingModel()
    temp_list = [12.5, 18.0]

    # Act（実行）
    result = forecast_visits(
        model, None, history_df, history_df["date"].max(), 2, temp_list=temp_list
    )

    # Assert（確認）
    assert len(result) == 2
    assert model.features[0]["temperature"].iloc[0] == 12.5
    assert model.features[1]["temperature"].iloc[0] == 18.0


def test_forecast_visits_uses_default_weather_when_weather_list_length_is_invalid():
    # Arrange（準備）
    history_df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=3),
        "visits": [10, 20, 30]
    })
    model = RecordingModel()
    le = LabelEncoder().fit(["晴", "曇", "雨"])
    weather_list = ["晴"]

    # Act（実行）
    result = forecast_visits(
        model, le, history_df, history_df["date"].max(), 2, weather_list=weather_list
    )

    # Assert（確認）
    assert len(result) == 2
    assert model.features[0]["weather_encoded"].iloc[0] == 0
    assert model.features[1]["weather_encoded"].iloc[0] == 0


def test_forecast_visits_uses_default_temperature_when_temp_list_length_is_invalid():
    # Arrange（準備）
    history_df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=3),
        "visits": [10, 20, 30]
    })
    model = RecordingModel()
    temp_list = [12.5]

    # Act（実行）
    result = forecast_visits(
        model, None, history_df, history_df["date"].max(), 2, temp_list=temp_list
    )

    # Assert（確認）
    assert len(result) == 2
    assert model.features[0]["temperature"].iloc[0] == 0.0
    assert model.features[1]["temperature"].iloc[0] == 0.0

def test_forecast_visits_30days():
    df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=30),
        "visits": range(30, 60),
        "weather": [
            "晴", "曇", "雨"
        ] * 10
    })
    model, le = train_lightgbm_model(df)
    last_date = df["date"].max()

    result = forecast_visits(
    model,
    le,
    df,
    last_date,
    30
    )

    assert len(result) == 30
    assert "date" in result.columns
    assert "predicted_visits" in result.columns
    assert result["date"].iloc[0] == last_date + pd.Timedelta(days=1)

def test_forecast_visits_90days():
    df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=30),
        "visits": range(30, 60),
        "weather": [
            "晴", "曇", "雨"
        ] * 10
    })
    model, le = train_lightgbm_model(df)
    last_date = df["date"].max()

    result = forecast_visits(
    model,
    le,
    df,
    last_date,
    90
    )

    assert len(result) == 90
    assert "date" in result.columns
    assert "predicted_visits" in result.columns
    assert result["date"].iloc[0] == last_date + pd.Timedelta(days=1)
##############################################################################
# forecast_visits() が predict() に渡す特徴量を確認するためのダミーモデル
class RecordingModel:
    def __init__(self):
        self.features = []

    def predict(self, feature):
        self.features.append(feature.copy())
        return [100]


def test_forecast_visits_uses_weather_list():
    # Arrange（準備）
    history_df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=30),
        "visits": range(30, 60),
        "weather": ["晴", "曇", "雨"] * 10,
        "temperature": [20.0 + i * 0.1 for i in range(30)]
    })

    model = RecordingModel()
    le = LabelEncoder().fit(["晴", "曇", "雨"])
    weather_list = ["晴", "曇"]

    # Act（実行）
    result = forecast_visits(
        model,
        le,
        history_df,
        history_df["date"].max(),
        2,
        weather_list=weather_list
    )

    # Assert（確認）
    assert len(result) == 2
    assert len(model.features) == 2
    assert model.features[0]["weather_encoded"].iloc[0] == le.transform(["晴"])[0]
    assert model.features[1]["weather_encoded"].iloc[0] == le.transform(["曇"])[0]


def test_forecast_visits_uses_temp_list():
    # Arrange（準備）
    history_df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=30),
        "visits": range(30, 60),
        "weather": ["晴", "曇", "雨"] * 10,
        "temperature": [20.0 + i * 0.1 for i in range(30)]
    })

    model = RecordingModel()
    temp_list = [12.5, 18.0]

    # Act（実行）
    result = forecast_visits(
        model,
        None,
        history_df,
        history_df["date"].max(),
        2,
        temp_list=temp_list
    )

    # Assert（確認）
    assert len(result) == 2
    assert len(model.features) == 2
    assert model.features[0]["temperature"].iloc[0] == 12.5
    assert model.features[1]["temperature"].iloc[0] == 18.0


def test_forecast_visits_uses_default_weather_when_weather_list_length_is_invalid():
    # Arrange（準備）
    history_df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=30),
        "visits": range(30, 60),
        "weather": ["晴", "曇", "雨"] * 10,
        "temperature": [20.0 + i * 0.1 for i in range(30)]
    })

    model = RecordingModel()
    le = LabelEncoder().fit(["晴", "曇", "雨"])
    weather_list = ["晴"]

    # Act（実行）
    result = forecast_visits(
        model,
        le,
        history_df,
        history_df["date"].max(),
        2,
        weather_list=weather_list
    )

    # Assert（確認）
    assert len(result) == 2
    assert len(model.features) == 2
    assert model.features[0]["weather_encoded"].iloc[0] == 0
    assert model.features[1]["weather_encoded"].iloc[0] == 0


def test_forecast_visits_uses_default_temperature_when_temp_list_length_is_invalid():
    # Arrange（準備）
    history_df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=30),
        "visits": range(30, 60),
        "weather": ["晴", "曇", "雨"] * 10,
        "temperature": [20.0 + i * 0.1 for i in range(30)]
    })

    model = RecordingModel()
    temp_list = [12.5]

    # Act（実行）
    result = forecast_visits(
        model,
        None,
        history_df,
        history_df["date"].max(),
        2,
        temp_list=temp_list
    )

    # Assert（確認）
    assert len(result) == 2
    assert len(model.features) == 2
    assert model.features[0]["temperature"].iloc[0] == 0.0
    assert model.features[1]["temperature"].iloc[0] == 0.0