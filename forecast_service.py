import pandas as pd

from db_service import get_visit_data
from lgbforecast import (
    train_lightgbm_model,
    forecast_visits
)


def forecast_from_db(store_id, forecast_days):

    #DBから取得
    df_db = get_visit_data(store_id)

    if df_db.empty:
        return None, None

    #前処理
    df_db["date"] = pd.to_datetime(df_db["date"])
    df_db = df_db.sort_values("date")

    #学習
    model, le = train_lightgbm_model(df_db)

    #予測
    last_date = df_db["date"].max()

    df_forecast = forecast_visits(
        model,
        le,
        last_date,
        forecast_days
    )

    return df_forecast, model