import pandas as pd
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder

#特徴量抽出
def create_features(df):
    df["dayofweek"] = df["date"].dt.dayofweek
    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    df["weekofyear"] = df["date"].dt.isocalendar().week.astype(int)

    return df

#モデル学習
def train_lightgbm_model(df):
    df = df.copy()
    df = create_features(df)

    #天気を数値に直す
    le = None

    if "weather" in df.columns:
        le = LabelEncoder()
        df["weather_encoded"] = le.fit_transform(df["weather"])
    else:
        df["weather_encoded"] = 0

    if "temperature" not in df.columns:
        df["temperature"] = 0.0

    #特徴量に追加
    X = df[["dayofweek", "day", "month", "weather_encoded", "temperature"]]
    y = df["visits"]

    model = lgb.LGBMRegressor(
    n_estimators=200,
    learning_rate=0.05,
    random_state=42
    )


    model.fit(X, y)
    if len(df) < 30:
        raise ValueError("学習データが少なすぎます")

    return model, le

#予測用関数の修正
def forecast_visits(model, le, last_date, forecast_days, weather_list=None, temp_list=None):
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days)

    future_df = pd.DataFrame({"date":future_dates})
    future_df = create_features(future_df)

#天気と気温のリスト
    if (
        le is not None
        and weather_list
        and len(weather_list) == forecast_days
):
        future_df["weather_encoded"] = le.transform(weather_list)

    else:
        future_df["weather_encoded"] = 0

    if temp_list and len(temp_list) == forecast_days:
        future_df["temperature"] = temp_list
    else:
        future_df["temperature"] =0.0

    X_future = future_df[['dayofweek', 'day', 'month', 'weather_encoded', 'temperature']]
    future_df["predicted_visits"] = model.predict(X_future).round()

    return future_df

