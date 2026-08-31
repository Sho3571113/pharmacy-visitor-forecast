import pandas as pd
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder

#特徴量抽出
def create_features(df):
    df = df.copy()

    df["dayofweek"] = df["date"].dt.dayofweek
    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    df["weekofyear"] = df["date"].dt.isocalendar().week.astype(int)
    
    if "visits" in df.columns:
        df["lag1"] = df["visits"].shift(1)
        df["rolling7"] = (
            df["visits"]
            .shift(1)
            .rolling(window=7, min_periods=1)
            .mean()
        )



    return df

#モデル学習
def train_lightgbm_model(df):
    if len(df) < 30:
        raise ValueError("学習データが少なすぎます")
    
    df = df.copy()
    df = create_features(df)
    df = df.dropna().reset_index(drop=True)

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
    X = df[["dayofweek", 
            "day",
            "month", 
            "lag1",
            "rolling7",
            "weather_encoded", 
            "temperature"]]
    
    y = df["visits"]

    model = lgb.LGBMRegressor(
    n_estimators=200,
    learning_rate=0.05,
    random_state=42
    )

    model.fit(X, y)
   

    return model, le

#予測用関数の修正
def forecast_visits(
        model,
        le, 
        history_df,
        last_date,
        forecast_days,
        weather_list=None,
        temp_list=None
):
    history = history_df.copy()

    results = []

    for i in range(forecast_days):

        target_date = last_date + pd.Timedelta(days=i + 1)

        lag1 = history["visits"].iloc[-1]
        rolling7 = history["visits"].tail(7).mean()

        feature = pd.DataFrame({
            "dayofweek": [target_date.dayofweek],
            "day": [target_date.day],
            "month": [target_date.month],
            "lag1": [lag1],
            "rolling7": [rolling7]
        })

                # 天気
        if (
            le is not None
            and weather_list
            and len(weather_list) == forecast_days
        ):
            feature["weather_encoded"] = le.transform([weather_list[i]])[0]
        else:
            feature["weather_encoded"] = 0

        # 気温
        if temp_list and len(temp_list) == forecast_days:
            feature["temperature"] = temp_list[i]
        else:
            feature["temperature"] = 0.0

        # 予測
        X_future = feature[
            [
                "dayofweek",
                "day",
                "month",
                "lag1",
                "rolling7",
                "weather_encoded",
                "temperature"
            ]
        ]

        pred = round(model.predict(X_future)[0])  

                # 結果を保存
        results.append({
            "date": target_date,
            "predicted_visits": pred
        })

        # 次の日の予測に使うため履歴へ追加
        history = pd.concat(
            [
                history,
                pd.DataFrame({
                    "date": [target_date],
                    "visits": [pred]
                })
            ],
            ignore_index=True
        )
    return pd.DataFrame(results)


