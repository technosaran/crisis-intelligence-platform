"use client";

import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  ComposedChart
} from "recharts";

export interface ChartDataPoint {
  day: string;
  actual?: number | null;
  moving_average?: number | null;
  linear_regression?: number | null;
  xgboost?: number | null;
  lstm?: number | null;
  lower_bound?: number | null;
  upper_bound?: number | null;
}

export function ForecastChart({ 
  data = [], 
  selectedModel = "all" 
}: { 
  data?: ChartDataPoint[]; 
  selectedModel?: string;
}) {
  const fallbackData: ChartDataPoint[] = [
    { day: "Day -3", actual: 320, moving_average: null, xgboost: null, lstm: null },
    { day: "Day -2", actual: 380, moving_average: null, xgboost: null, lstm: null },
    { day: "Day -1", actual: 440, moving_average: null, xgboost: null, lstm: null },
    { day: "Today", actual: 520, moving_average: 500, xgboost: 530, lstm: 540 },
    { day: "Day +1", actual: null, moving_average: 550, linear_regression: 580, xgboost: 680, lstm: 710, lower_bound: 580, upper_bound: 780 },
    { day: "Day +2", actual: null, moving_average: 590, linear_regression: 640, xgboost: 840, lstm: 890, lower_bound: 710, upper_bound: 970 },
    { day: "Day +3", actual: null, moving_average: 620, linear_regression: 700, xgboost: 990, lstm: 1050, lower_bound: 840, upper_bound: 1140 },
  ];

  const chartData = data.length > 0 ? data : fallbackData;

  const showAll = selectedModel === "all";
  const showMA = showAll || selectedModel === "moving_average";
  const showLR = showAll || selectedModel === "linear_regression";
  const showXGB = showAll || selectedModel === "xgboost";
  const showLSTM = showAll || selectedModel === "lstm";

  return (
    <div className="h-[420px] w-full mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={chartData}
          margin={{
            top: 15,
            right: 30,
            left: 20,
            bottom: 10,
          }}
        >
          <defs>
            <linearGradient id="confidenceBand" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.25}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.02}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} stroke="#94a3b8" />
          <XAxis 
            dataKey="day" 
            stroke="#64748b" 
            fontSize={11} 
            tickLine={false} 
            axisLine={{ stroke: '#cbd5e1' }} 
          />
          <YAxis 
            stroke="#64748b" 
            fontSize={11} 
            tickLine={false} 
            axisLine={{ stroke: '#cbd5e1' }} 
            tickFormatter={(val) => `${val}`}
          />
          <Tooltip 
            contentStyle={{ 
              borderRadius: '8px', 
              border: '1px solid #e2e8f0', 
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              fontSize: '12px'
            }}
            formatter={(value: any) => [`${value} units`, ""]}
          />
          <Legend wrapperStyle={{ paddingTop: '16px', fontSize: '12px' }} />
          
          {/* Upper bound confidence fill */}
          {showXGB && (
            <Area
              type="monotone"
              dataKey="upper_bound"
              name="95% Confidence Band"
              stroke="none"
              fill="url(#confidenceBand)"
            />
          )}

          {/* Actual Historical Line */}
          <Line
            type="monotone"
            dataKey="actual"
            name="Observed Telemetry"
            stroke="#0f172a"
            strokeWidth={3}
            dot={{ r: 4, fill: '#0f172a' }}
            activeDot={{ r: 6 }}
            connectNulls={false}
          />

          {/* Moving Average */}
          {showMA && (
            <Line
              type="monotone"
              dataKey="moving_average"
              name="Moving Average Baseline"
              stroke="#94a3b8"
              strokeWidth={2}
              strokeDasharray="4 4"
              dot={{ r: 3 }}
            />
          )}

          {/* Linear Regression */}
          {showLR && (
            <Line
              type="monotone"
              dataKey="linear_regression"
              name="Linear Trend Model"
              stroke="#f59e0b"
              strokeWidth={2}
              strokeDasharray="6 3"
              dot={{ r: 3 }}
            />
          )}

          {/* XGBoost */}
          {showXGB && (
            <Line
              type="monotone"
              dataKey="xgboost"
              name="XGBoost Non-Linear Regressor"
              stroke="#2563eb"
              strokeWidth={3}
              dot={{ r: 4, fill: '#2563eb' }}
            />
          )}

          {/* PyTorch LSTM */}
          {showLSTM && (
            <Line
              type="monotone"
              dataKey="lstm"
              name="PyTorch LSTM Deep Forecaster"
              stroke="#8b5cf6"
              strokeWidth={3}
              dot={{ r: 4, fill: '#8b5cf6' }}
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

