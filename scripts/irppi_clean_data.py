import pandas as pd

df = pd.read_csv('/mnt/user-data/uploads/HPM06_20260612071320.csv')

# Keep only the actual index level (not pre-computed % changes - we'll derive these)
df = df[df['Statistic Label'] == 'Residential Property Price Index'].copy()

# Parse date
df['Date'] = pd.to_datetime(df['Month'], format='%Y %B')

# Keep relevant columns
df = df[['Date', 'Type of Residential Property', 'VALUE']]
df.columns = ['Date', 'Region_Type', 'Index_Value']

# Drop rows with missing values (mostly older county-level rows before they started reporting)
df = df.dropna(subset=['Index_Value'])
df['Index_Value'] = pd.to_numeric(df['Index_Value'])

# Phase 1: National + Dublin/non-Dublin split
phase1_categories = [
    'National - all residential properties',
    'National - houses',
    'National - apartments',
    'Dublin - all residential properties',
    'Dublin - houses',
    'Dublin - apartments',
    'National excluding Dublin - all residential properties',
    'National excluding Dublin - houses',
    'National excluding Dublin - apartments'
]

phase1 = df[df['Region_Type'].isin(phase1_categories)].copy()

# Pivot wide: one column per region/type
phase1_wide = phase1.pivot(index='Date', columns='Region_Type', values='Index_Value').reset_index()
phase1_wide = phase1_wide.sort_values('Date')

# Calculate month-over-month % change and 12-month % change for the "all properties" series
for col in ['National - all residential properties', 'Dublin - all residential properties',
            'National excluding Dublin - all residential properties']:
    phase1_wide[f'{col} MoM %'] = phase1_wide[col].pct_change() * 100
    phase1_wide[f'{col} YoY %'] = phase1_wide[col].pct_change(12) * 100

phase1_wide.to_csv('/home/claude/rppi_national_dublin.csv', index=False)
print("Saved. Shape:", phase1_wide.shape)
print(phase1_wide.tail())
