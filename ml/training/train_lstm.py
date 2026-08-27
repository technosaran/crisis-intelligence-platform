import os
import sys
import torch
import torch.nn as nn
import pandas as pd
import numpy as np

# Ensure backend imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from app.intelligence.forecasting.lstm import LSTMModel

def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        xs.append(data[i:(i + seq_length)])
        ys.append(data[i + seq_length])
    return np.array(xs), np.array(ys)

def train_offline():
    print("Generating synthetic historical data for offline training...")
    # Generate 1000 days of synthetic demand data with some seasonality and noise
    t = np.arange(1000)
    base_demand = 500
    seasonality = 200 * np.sin(2 * np.pi * t / 365) # Yearly
    noise = np.random.normal(0, 50, 1000)
    data = base_demand + seasonality + noise
    
    # Normalize
    data_min = np.min(data)
    data_max = np.max(data)
    data_normalized = (data - data_min) / (data_max - data_min)
    
    seq_length = 5
    X, y = create_sequences(data_normalized, seq_length)
    
    X_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(-1)
    y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(-1)
    
    print("Initializing LSTM model architecture...")
    model = LSTMModel(input_size=1, hidden_size=16, num_layers=1, output_size=1)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    
    epochs = 200
    print(f"Training for {epochs} epochs...")
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad(set_to_none=True)
        output = model(X_tensor)
        loss = criterion(output, y_tensor)
        loss.backward()
        optimizer.step()
        
        if (epoch+1) % 50 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")
            
    # Save the weights
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../models'))
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, 'lstm_v1.pt')
    
    torch.save(model.state_dict(), model_path)
    print(f"Offline training complete. Model saved to {model_path}")

if __name__ == "__main__":
    train_offline()
