import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from utils import adstock, logistic_saturation

def prepare_features(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    df["adstock_spend"] = adstock(df["spend"], rate=0.4)
    df["sat_spend"] = logistic_saturation(df["spend"])

    df["lag_revenue"] = df["revenue"].shift(1)
    df["day_of_week"] = df["date"].dt.dayofweek

    df = df.dropna()
    return df

def train_model(df):
    df = prepare_features(df)
    X = df[["adstock_spend", "sat_spend", "lag_revenue", "day_of_week"]]
    y = df["revenue"]

    model = RandomForestRegressor(n_estimators=200)
    model.fit(X, y)
    return model

def run_forecast(df, days=30, budget_adjustment=0):
    df = df.copy()
    model = train_model(df)

    last_row = prepare_features(df).iloc[-1:].copy()
    forecasts = []

    for _ in range(days):
        new = last_row.copy()
        new["spend"] *= (1 + budget_adjustment)

        new["adstock_spend"] = adstock(new["spend"], rate=0.4)[-1]
        new["sat_spend"] = logistic_saturation(new["spend"])[-1]
        new["lag_revenue"] = new["revenue"]
        new["day_of_week"] = (new["date"].dt.dayofweek + 1) % 7

        X_new = new[["adstock_spend", "sat_spend", "lag_revenue", "day_of_week"]]
        pred = model.predict(X_new)[0]

        new["revenue"] = pred
        new["date"] += pd.Timedelta(days=1)

        forecasts.append({
            "date": new["date"].values[0],
            "predicted_revenue": float(pred)
        })

        last_row = new

    return forecasts
