"""
Exploratory Data Analysis: Irish Residential Property Price Index
Generates trend plots for National, Dublin, and Rest-of-Ireland price indices.
"""

import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/rppi_national_dublin.csv', parse_dates=['Date'])

print("=== Summary Stats (Index Values) ===")
print(df[['National - all residential properties',
          'Dublin - all residential properties',
          'National excluding Dublin - all residential properties']].describe())

print("\n=== Recent YoY % (last 6 months) ===")
yoy_cols = [c for c in df.columns if 'YoY' in c]
print(df[['Date'] + yoy_cols].tail(6).to_string(index=False))

# Plot: Index level and YoY % side by side
fig, ax = plt.subplots(1, 2, figsize=(14, 5))

ax[0].plot(df['Date'], df['National - all residential properties'], label='National')
ax[0].plot(df['Date'], df['Dublin - all residential properties'], label='Dublin')
ax[0].plot(df['Date'], df['National excluding Dublin - all residential properties'], label='Non-Dublin')
ax[0].set_title('Residential Property Price Index (2005-2026)')
ax[0].axhline(100, color='gray', linestyle='--', alpha=0.5)
ax[0].legend()

ax[1].plot(df['Date'], df['National - all residential properties YoY %'], label='National')
ax[1].plot(df['Date'], df['Dublin - all residential properties YoY %'], label='Dublin')
ax[1].plot(df['Date'], df['National excluding Dublin - all residential properties YoY %'], label='Non-Dublin')
ax[1].set_title('Year-over-Year % Change')
ax[1].axhline(0, color='gray', linestyle='--', alpha=0.5)
ax[1].legend()

plt.tight_layout()
plt.savefig('images/irppi_eda_trends.png', dpi=100)
print("\nSaved plot to images/irppi_eda_trends.png")
