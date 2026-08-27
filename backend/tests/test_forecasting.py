import pytest
from datetime import datetime, timedelta
from app.intelligence.forecasting.baselines import BaselineForecaster
from app.intelligence.forecasting.lstm import LSTMForecaster
import numpy as np

class MockDemandRecord:
    def __init__(self, timestamp, quantity):
        self.timestamp = timestamp
        self.quantity = quantity

def test_moving_average_forecaster():
    forecaster = BaselineForecaster()
    base_date = datetime.utcnow() - timedelta(days=10)
    mock_records = [MockDemandRecord(base_date + timedelta(days=i), 100 + i*10) for i in range(10)]
    df = forecaster.prepare_data(mock_records)
    predictions = forecaster.moving_average(df, horizon=3, window=3)
    assert len(predictions) == 3
    assert "MA_window_3" in predictions[0]["model_version"]

def test_linear_regression_forecaster():
    forecaster = BaselineForecaster()
    base_date = datetime.utcnow() - timedelta(days=10)
    mock_records = [MockDemandRecord(base_date + timedelta(days=i), 100 + i*10) for i in range(10)]
    df = forecaster.prepare_data(mock_records)
    predictions = forecaster.linear_regression(df, horizon=3)
    assert len(predictions) == 3

def test_xgboost_forecaster():
    forecaster = BaselineForecaster()
    base_date = datetime.utcnow() - timedelta(days=10)
    mock_records = [MockDemandRecord(base_date + timedelta(days=i), 100 + i*10) for i in range(10)]
    df = forecaster.prepare_data(mock_records)
    predictions = forecaster.xgboost_forecast(df, horizon=3)
    assert len(predictions) == 3

def test_lstm_sequences():
    lstm = LSTMForecaster()
    data = np.array([1, 2, 3, 4, 5, 6, 7])
    X, y = lstm.create_sequences(data, seq_length=3)
    assert len(X) == 4
    assert list(X[0]) == [1, 2, 3]
    assert y[0] == 4

def test_lstm_forecaster():
    forecaster = BaselineForecaster()
    lstm = LSTMForecaster()
    base_date = datetime.utcnow() - timedelta(days=20) # Need more data for sequence len 5
    mock_records = [MockDemandRecord(base_date + timedelta(days=i), 100 + i*5) for i in range(20)]
    df = forecaster.prepare_data(mock_records)
    
    predictions = lstm.train_and_predict(df, horizon=3, seq_length=5, epochs=2)
    assert len(predictions) == 3
    assert "LSTM_v1" in predictions[0]["model_version"]
