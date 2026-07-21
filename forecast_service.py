import pandas as pd
import joblib

from db_service import get_visit_data,   save_forecast_result
from lgbforecast import (
    train_lightgbm_model,
    forecast_visits
)

MODEL_PATH = "saved_models/model.pkl"
LABEL_ENCODER_PATH = "saved_models/label_encoder.pkl"


def forecast_from_db(store_id, forecast_days):

    #DBから取得
    df_db = get_visit_data(store_id)

    if df_db.empty:
        return None, None

    #前処理
    df_db["date"] = pd.to_datetime(df_db["date"])
    df_db = df_db.sort_values("date")

    # 保存済みモデルを読み込む
    try:
        model = joblib.load(MODEL_PATH)
        le = joblib.load(LABEL_ENCODER_PATH)
    except FileNotFoundError:
        return None, None

    #予測
    last_date = df_db["date"].max()
    #最終日確認
    print(last_date)

    df_forecast = forecast_visits(
        model,
        le,
        df_db,
        last_date,
        forecast_days
    )
    if df_forecast is None:
        return None, model

    for _, row in df_forecast.iterrows():
        save_forecast_result(
            store_id,
            row["date"],
            row["predicted_visits"]
        )

    return df_forecast, model

def train_model_from_db(store_id):
    df_db = get_visit_data(store_id)
    if df_db.empty:
        return False
    
    df_db["date"] = pd.to_datetime(df_db["date"])
    df_db = df_db.sort_values("date")

    model, le = train_lightgbm_model(df_db)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(le, LABEL_ENCODER_PATH)

    return True