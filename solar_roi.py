# Calculate return on investment of solar panels

import pandas as pd



# import csv file generate from NREL PV_Watts Calculator
df = pd.read_csv('pvwatts_hourly.csv', skiprows = 31)
print(df)

# Assume no power is used by home. All power is sold back to grid. Calculate value of solar energy.

# D1.11

# D1.2

# Loop through each month of the year, then each day, then each hour.
#for i in range()
#for i in range(0,len(df.index)):
for i in range(0,24):
    # print(df.iloc[0])
    print(df.iloc[i][11]/1000)

# Create price vector, which ultimately will be multiplied by power vector
# Price vector will have 4 values

