# Calculate return on investment (ROI) of solar panels. 

# Assume no power is used by home. All power is sold back to grid. Calculate 
# value of annual solar energy production. Divide cost of solar panel 
# installation by annual solar energy production income to get ROI.

import pandas as pd
import numpy as np

# Create class to calculate electricity rates purchase and sell back rates
# DTE Residential Electric Pricing Options: 
# https://newlook.dteenergy.com/wps/wcm/connect/23195474-a4d1-4d38-aa30-a4426fd3336b/WholeHouseRateOptions.pdf?MOD=AJPERES

class Rate:
  def __init__(self, name, pscr, distr):
    self.name = name
    self.pscr = pscr
    self.distr = distr
    self.smmr = [0, 0] # Define summer months
    self.peak = [0, 0] # Define peak hours
    self.smmr_peak_cap = 0
    self.smmr_peak_ncp = 0
    self.smmr_offpk_cap = 0
    self.smmr_offpk_ncp = 0
    self.wntr_peak_cap = 0
    self.wntr_peak_ncp = 0
    self.wntr_offpk_cap = 0
    self.wntr_offpk_ncp = 0
    self.smmr_peak_sell = 0
    self.smmr_offpk_sell = 0
    self.wntr_peak_sell = 0
    self.wntr_offpk_sell = 0
    self.smmr_peak_buy = 0
    self.smmr_offpk_buy = 0
    self.wntr_peak_buy = 0
    self.wntr_offpk_buy = 0

  def calc_rates(self):
    # Calculate cost to purchase and sell back electricity in the summer and 
    # winter during on-peak and off-peak hours
    self.smmr_peak_sell = self.smmr_peak_cap + self.smmr_peak_ncp + self.pscr
    self.smmr_offpk_sell = self.smmr_offpk_cap + self.smmr_offpk_ncp + self.pscr
    self.wntr_peak_sell = self.wntr_peak_cap + self.wntr_peak_ncp + self.pscr
    self.wntr_offpk_sell = self.wntr_offpk_cap + self.wntr_offpk_ncp + self.pscr
    self.smmr_peak_buy = self.smmr_peak_sell + self.distr
    self.smmr_offpk_buy = self.smmr_offpk_sell + self.distr
    self.wntr_peak_buy = self.wntr_peak_sell + self.distr
    self.wntr_offpk_buy = self.wntr_offpk_sell + self.distr
    # Print purchase rates
    print(self.name + " Purchase Rates")
    print("\tSummer Peak: %.3f" % self.smmr_peak_buy)
    print("\tSummer OffP: %.3f" % self.smmr_offpk_buy)
    print("\tWinter Peak: %.3f" % self.wntr_peak_buy)
    print("\tWinter OffP: %.3f" % self.wntr_offpk_buy + "\n")

# Time-invariant Costs
pscr = 1.917 # Power Supply Cost Recovery
distr = 6.879 # Distributions

# Time of Day 3 p.m. – 7 p.m. Standard Base Rate (D1.11) 
D1_11 = Rate("D1_11",pscr, distr)
D1_11.smmr = [6, 9]
D1_11.peak = [15, 19]
D1_11.smmr_peak_cap = 7.941
D1_11.smmr_peak_ncp = 6.160
D1_11.smmr_offpk_cap = 4.828
D1_11.smmr_offpk_ncp = 3.746
D1_11.wntr_peak_cap = 5.560
D1_11.wntr_peak_ncp = 4.313
D1_11.wntr_offpk_cap = 4.828
D1_11.wntr_offpk_ncp = 3.746
D1_11.calc_rates()

# Time of Day 11 a.m. - 7 p.m. Rate (D1.2) 
D1_2 = Rate("D1_2", pscr, distr)
D1_2.smmr = [6, 10]
D1_2.peak = [11, 19]
D1_2.smmr_peak_cap = 11.033
D1_2.smmr_peak_ncp = 4.105
D1_2.smmr_offpk_cap = 0.991
D1_2.smmr_offpk_ncp = 4.105
D1_2.wntr_peak_cap = 8.682
D1_2.wntr_peak_ncp = 4.105
D1_2.wntr_offpk_cap = 0.792
D1_2.wntr_offpk_ncp = 4.105
D1_2.calc_rates()

# Import hourly solar energy generation csv file created by NREL PV_Watts Calculator
df = pd.read_csv("pvwatts_hourly.csv", skiprows=31)

# Add two empty columns to the dataframe for each rate option: One to capture electric 
# sellback rate (¢/kWh) each hour and another to capture hourly profit
df["D1_11_rate"] = np.nan
df["D1_11_profit"] = np.nan
df["D1_2_rate"] = np.nan
df["D1_2_profit"] = np.nan

def calc_hourly_sellback_rate(rate):
    # Calculate the price of selling back electricity to the grid for each hour 
    # of each day of the year
    if (month < rate.smmr[0]) or (month > rate.smmr[1]):
        # winter
        if (hour < rate.peak[0]) or (hour > rate.peak[1]):
            # off peak
            df.iloc[i, df.columns.get_loc(rate.name + "_rate")] = rate.wntr_offpk_sell
        else:
            # on peak
            df.iloc[i, df.columns.get_loc(rate.name  + "_rate")] = rate.wntr_peak_sell
    else:
        # summer
        if (hour < rate.peak[0]) or (hour > rate.peak[1]):
            # off peak
            df.iloc[i, df.columns.get_loc(rate.name  + "_rate")] = rate.smmr_offpk_sell
        else:
            # on peak
            df.iloc[i, df.columns.get_loc(rate.name  + "_rate")] = rate.smmr_peak_sell

# Calculate the hourly electricity sellback rate for each rate option (i.e. 
# D1.11 and D1.2)
for i in range(0, len(df.index)):
    hour = df.iloc[i][2]
    month = df.iloc[i][0]
    calc_hourly_sellback_rate(D1_11)
    calc_hourly_sellback_rate(D1_2)

# Get the product of the hourly energy production in kWh and the hourly sellback
# rate in $/kWh
df["D1_11_profit"] = df["AC System Output (W)"] / 1000 * df["D1_11_rate"] / 100
df["D1_2_profit"] = df["AC System Output (W)"] / 1000 * df["D1_2_rate"] / 100
D1_11_profit = df["D1_11_profit"].sum()
D1_2_profit = df["D1_2_profit"].sum()

# Print the results
print("Annual profit selling all electricity back to DTE:")
print("\t D1_11: $" + '{:0,.2f}'.format(D1_11_profit))
print("\t D1_02: $" + '{:0,.2f}'.format(D1_2_profit))

Cost = 35000
print("\nROI (years):")
print("\t D1_11: " + '{:0,.1f}'.format(Cost/D1_11_profit))
print("\t D1_02: " + '{:0,.1f}'.format(Cost/D1_2_profit))