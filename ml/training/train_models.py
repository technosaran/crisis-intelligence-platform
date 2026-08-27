"""
Model Training & Experimentation Pipeline for Crisis Resource Forecasting.
Trains baseline (Linear Regression), tree-based (XGBoost), and deep learning (PyTorch LSTM)
models on historical disaster sequences.
"""

import pandas as pd
import numpy as np
import os
import torch
import torch.nn as nn
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb

from ml.datasets.generate_disaster_dataset import generate_crisis_dataset

class PyTorchLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=16, num_layers=1, output_size=1):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.1 if num_layers > 1 else 0)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

def train_and_evaluate_all():
    dataset_path = "ml/datasets/crisis_demand_historical.csv"
    if not os.path.exists(dataset_path):
        df = generate_crisis_dataset(output_path=dataset_path)
    else:
        df = pd.read_csv(dataset_path)

    # Filter for Zone 1, Insulin for focused benchmark
    sub_df = df[(df["location_id"] == 1) & (df["resource_id"] == 1)].sort_values("day_index").copy()
    
    train_size = int(len(sub_df) * 0.8)
    train_df = sub_df.iloc[:train_size]
    test_df = sub_df.iloc[train_size:]
    
    y_train = train_df["demand_quantity"].values
    y_test = test_df["demand_quantity"].values
    
    results = {}
    
    # 1. Moving Average
    window = 3
    ma_preds = []
    hist = list(y_train)
    for _ in range(len(y_test)):
        ma_val = np.mean(hist[-window:])
        ma_preds.append(ma_val)
        hist.append(ma_val)
    ma_preds = np.array(ma_preds)
    
    # 2. Linear Regression
    lr = LinearRegression()
    lr.fit(train_df[["day_index", "day_of_week"]], y_train)
    lr_preds = lr.predict(test_df[["day_index", "day_of_week"]])
    
    # 3. XGBoost
    xgb_model = xgb.XGBRegressor(n_estimators=150, max_depth=4, learning_rate=0.05, random_state=42)
    xgb_model.fit(train_df[["day_index", "day_of_week", "is_disaster_active"]], y_train)
    xgb_preds = xgb_model.predict(test_df[["day_index", "day_of_week", "is_disaster_active"]])
    
    # 4. PyTorch LSTM
    seq_len = 5
    def make_seqs(data, s_len):
        xs, ys = [], []
        for i in range(len(data) - s_len):
            xs.append(data[i:(i + s_len)])
            ys.append(data[i + s_len])
        return np.array(xs), np.array(ys)
        
    d_min, d_max = y_train.min(), y_train.max()
    norm_train = (y_train - d_min) / (d_max - d_min + 1e-5)
    
    X_tr, y_tr = make_seqs(norm_train, seq_len)
    X_t_tensor = torch.tensor(X_tr, dtype=torch.float32).unsqueeze(-1)
    y_t_tensor = torch.tensor(y_tr, dtype=torch.float32).unsqueeze(-1)
    
    lstm = PyTorchLSTM(input_size=1, hidden_size=16, num_layers=1)
    optimizer = torch.optim.Adam(lstm.parameters(), lr=0.01)
    criterion = nn.MSELoss()
    
    lstm.train()
    for ep in range(60):
        optimizer.zero_grad()
        out = lstm(X_t_tensor)
        loss = criterion(out, y_t_tensor)
        loss.backward()
        optimizer.step()
        
    lstm.eval()
    curr_seq = norm_train[-seq_len:]
    lstm_norm_preds = []
    with torch.no_grad():
        for _ in range(len(y_test)):
            in_t = torch.tensor(curr_seq, dtype=torch.float32).unsqueeze(0).unsqueeze(-1)
            p = lstm(in_t).item()
            lstm_norm_preds.append(p)
            curr_seq = np.append(curr_seq[1:], p)
            
    lstm_preds = np.array(lstm_norm_preds) * (d_max - d_min + 1e-5) + d_min

    # Calculate metrics
    models = {
        "Moving Average (Baseline)": ma_preds,
        "Linear Regression": lr_preds,
        "XGBoost Regressor": xgb_preds,
        "PyTorch LSTM": lstm_preds
    }
    
    print("\n" + "="*70)
    print("CRISIS DEMAND FORECASTING BENCHMARK RESULTS")
    print("="*70)
    print(f"{'Model Architecture':<30} | {'RMSE':<8} | {'MAE':<8} | {'MAPE (%)':<10} | {'R2 Score':<8}")
    print("-"*70)
    
    for name, p in models.items():
        rmse = np.sqrt(mean_squared_error(y_test, p))
        mae = mean_absolute_error(y_test, p)
        mape = np.mean(np.abs((y_test - p) / np.maximum(y_test, 1.0))) * 100
        r2 = r2_score(y_test, p)
        results[name] = {"rmse": round(rmse, 2), "mae": round(mae, 2), "mape": round(mape, 2), "r2": round(r2, 3)}
        print(f"{name:<30} | {rmse:<8.2f} | {mae:<8.2f} | {mape:<10.2f} | {r2:<8.3f}")
        
    print("="*70 + "\n")
    return results

if __name__ == "__main__":
    train_and_evaluate_all()
