import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.linear_model import LinearRegression
import xgboost as xgb


class BaselineForecaster:
    """Statistical baseline forecasters for demand prediction comparison."""

    def prepare_data(self, demand_records) -> pd.DataFrame:
        """Convert raw demand records to aggregated daily DataFrame."""
        data = []
        for r in demand_records:
            data.append({
                "date": r.timestamp.date() if hasattr(r.timestamp, 'date') else r.timestamp,
                "quantity": float(r.quantity)
            })
        df = pd.DataFrame(data)
        if df.empty:
            return df
        df = df.groupby("date")["quantity"].sum().reset_index()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values("date")

        if len(df) > 0:
            idx = pd.date_range(df['date'].min(), df['date'].max())
            df = df.set_index('date').reindex(idx, fill_value=0.0).rename_axis('date').reset_index()
        return df

    def moving_average(self, df: pd.DataFrame, horizon: int, window: int = 3) -> list:
        """Simple Moving Average forecast."""
        if df.empty or len(df) < window:
            return []

        data = df['quantity'].values
        last_date = df['date'].iloc[-1]
        current_window = list(data[-window:])
        predictions = []

        for i in range(horizon):
            avg = float(np.mean(current_window))
            pred_val = round(max(0.0, avg), 2)
            pred_date = last_date + timedelta(days=i + 1)

            predictions.append({
                "forecast_timestamp": pred_date,
                "predicted_demand": pred_val,
                "lower_bound": round(max(0.0, pred_val * 0.80), 2),
                "upper_bound": round(pred_val * 1.20, 2),
                "confidence": 0.65,
                "model_version": f"MA_window_{window}"
            })
            current_window.pop(0)
            current_window.append(avg)

        return predictions

    def linear_regression(self, df: pd.DataFrame, horizon: int) -> list:
        """Linear Regression trend forecast."""
        if df.empty or len(df) < 3:
            return []

        data = df['quantity'].values
        last_date = df['date'].iloc[-1]
        X = np.arange(len(data)).reshape(-1, 1)
        y = data

        model = LinearRegression()
        model.fit(X, y)

        predictions = []
        for i in range(horizon):
            future_x = np.array([[len(data) + i]])
            pred_val = round(max(0.0, float(model.predict(future_x)[0])), 2)
            pred_date = last_date + timedelta(days=i + 1)

            predictions.append({
                "forecast_timestamp": pred_date,
                "predicted_demand": pred_val,
                "lower_bound": round(max(0.0, pred_val * 0.82), 2),
                "upper_bound": round(pred_val * 1.18, 2),
                "confidence": 0.75,
                "model_version": "LinearRegression_v1"
            })
        return predictions

    def xgboost_forecast(self, df: pd.DataFrame, horizon: int, n_lags: int = 5) -> list:
        """XGBoost Regressor with lag features."""
        if df.empty or len(df) < n_lags + 3:
            return []

        data = df['quantity'].values
        last_date = df['date'].iloc[-1]

        # Create lag features
        X, y = [], []
        for i in range(n_lags, len(data)):
            X.append(data[i - n_lags:i])
            y.append(data[i])
        X = np.array(X)
        y = np.array(y)

        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            objective='reg:squarederror',
            verbosity=0
        )
        model.fit(X, y)

        # Predict forward
        predictions = []
        current_lags = list(data[-n_lags:])
        for i in range(horizon):
            features = np.array([current_lags[-n_lags:]])
            pred_val = round(max(0.0, float(model.predict(features)[0])), 2)
            pred_date = last_date + timedelta(days=i + 1)

            predictions.append({
                "forecast_timestamp": pred_date,
                "predicted_demand": pred_val,
                "lower_bound": round(max(0.0, pred_val * 0.88), 2),
                "upper_bound": round(pred_val * 1.12, 2),
                "confidence": 0.90,
                "model_version": "XGBoost_v1"
            })
            current_lags.append(pred_val)

        return predictions


baseline_forecaster = BaselineForecaster()
