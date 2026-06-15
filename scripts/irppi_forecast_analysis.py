"""
6-Month Forecast: Irish Residential Property Price Index
Uses 12-month trailing CAGR (compound monthly growth rate) extrapolation
for National, Dublin, and Rest-of-Ireland price indices.
"""

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/rppi_national_dublin.csv', parse_dates=['Date'])
df = df.set_index('Date')

series_map = {
    'National': 'National - all residential properties',
    'Dublin': 'Dublin - all residential properties',
    'Non-Dublin': 'National excluding Dublin - all residential properties'
}

forecast_horizon = 6
future_dates = pd.date_range(start=df.index[-1] + pd.DateOffset(months=1),
                              periods=forecast_horizon, freq='MS')
forecast_df = pd.DataFrame(index=future_dates)
forecast_df.index.name = 'Date'

for name, col in series_map.items():
    series = df[col]
    # Average monthly growth rate over last 12 months (recent momentum)
    recent = series.iloc[-13:]
    monthly_growth = (recent.iloc[-1] / recent.iloc[0]) ** (1 / 12) - 1
    last_val = series.iloc[-1]
    forecast_vals = [last_val * (1 + monthly_growth) ** (i + 1) for i in range(forecast_horizon)]
    forecast_df[name] = forecast_vals
    print(f"{name}: last actual = {last_val:.1f}, monthly growth = {monthly_growth*100:.2f}%, "
          f"+6mo forecast = {forecast_vals[-1]:.1f}")

forecast_df.to_csv('data/rppi_forecast.csv')

# Plot: last 3 years + 6-month forecast
fig, ax = plt.subplots(figsize=(10, 5))
for name, col in series_map.items():
    ax.plot(df.index[-36:], df[col].iloc[-36:], label=f'{name} (actual)')
    ax.plot(forecast_df.index, forecast_df[name], '--', label=f'{name} (forecast)')
ax.set_title('RPPI: Last 3 Years + 6-Month Forecast (Trend Extrapolation)')
ax.set_ylabel('Index (Jan 2005 = 100)')
ax.legend()
plt.tight_layout()
plt.savefig('images/irppi_forecast_plot.png', dpi=100)
print("Saved plot to images/irppi_forecast_plot.png")
