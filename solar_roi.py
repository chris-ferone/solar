"""
Calculate the payback period of a 20kW ground mount solar panel 
array facing due south in Ann Arbor, MI.

Consider the extremes. In one scenario, assume no power generated by the array 
is used by the home. Instead, all power is sold back to grid. Calculate the 
value of the annual solar energy production. Divide cost of solar panel 
installation by annual solar energy production income to get payback period. In another 
scenario, assume no power is sold back to the grid; all energy produced by the 
solar array is used by the home. Calculate the value of the energy that did not 
need to be purchased. Divide cost of solar panel installation by annual avoided 
energy cost get payback period. The actual payback period will lie somewhere between these two 
extremes based on how well the timing of solar energy production and home energy
consumption align.
"""

import pandas as pd
import numpy as np
import json
 
# Open JSON file containing electricity rates
f = open('electricity_rates.json')
# Returns JSON object as a dictionary
elctr_rates = json.load(f) 
# Close file
f.close()

# Open JSON file containing solar array information
f = open('solar_params.json')
# Returns JSON object as a dictionary
solar_info = json.load(f) 
# Close file
f.close()

# Create class to calculate electricity rates purchase and sell back rates
# DTE Residential Electric Pricing Options:
# https://newlook.dteenergy.com/wps/wcm/connect/23195474-a4d1-4d38-aa30-a4426fd3336b/WholeHouseRateOptions.pdf?MOD=AJPERES

class Rate:
    def __init__(self, name, elctr_rates):
        pscr = elctr_rates['time_invariant_costs'][0]['pscr']
        self.distr = elctr_rates['time_invariant_costs'][0]['distr']

        for rate in elctr_rates['time_varying_costs']:
            if rate['name'] == name:
                self.name = rate['name']              
                if name == 'D1_8':
                    self.peak = rate['peak_hours']
                    self.mdpeak = rate['mdpeak_hours']
                    self.peak_sell = rate['peak_cap'] + rate['peak_ncp'] + pscr
                    self.midpk_sell = rate['midpk_cap'] + rate['midpk_ncp'] + pscr
                    self.offpk_sell = rate['offpk_cap'] + rate['offpk_ncp'] + pscr
                    self.peak_buy = self.peak_sell + self.distr
                    self.midpk_buy = self.midpk_sell + self.distr  
                    self.offpk_buy = self.offpk_sell + self.distr  
                    # Print purchase rates
                    if False:
                        print(self.name + " Purchase Rates")
                        print("\tPeak: %.3f" % self.peak_buy)
                        print("\tMid Peak: %.3f" % self.midpk_buy)
                        print("\tOff Peak: %.3f" % self.offpk_buy + "\n")
                if name == "D1_11" or name == "D1_2":
                    self.smmr = rate['smmr_mnths']
                    self.peak = rate['peak_hours']
                    # Calculate cost to purchase and sell back electricity in the summer and
                    # winter during on-peak and off-peak hours
                    self.smmr_peak_sell = rate['smmr_peak_cap'] + rate['smmr_peak_ncp'] + pscr
                    self.smmr_offpk_sell = rate['smmr_offpk_cap'] + rate['smmr_offpk_ncp'] + pscr
                    self.wntr_peak_sell = rate['wntr_peak_cap'] + rate['wntr_peak_ncp'] + pscr
                    self.wntr_offpk_sell = rate['wntr_offpk_cap'] + rate['wntr_offpk_ncp'] + pscr
                    self.smmr_peak_buy = self.smmr_peak_sell + self.distr
                    self.smmr_offpk_buy = self.smmr_offpk_sell + self.distr
                    self.wntr_peak_buy = self.wntr_peak_sell + self.distr
                    self.wntr_offpk_buy = self.wntr_offpk_sell + self.distr
                    # Print purchase rates
                    if False:
                        print(self.name + " Purchase Rates")
                        print("\tSummer Peak: %.3f" % self.smmr_peak_buy)
                        print("\tSummer OffP: %.3f" % self.smmr_offpk_buy)
                        print("\tWinter Peak: %.3f" % self.wntr_peak_buy)
                        print("\tWinter OffP: %.3f" % self.wntr_offpk_buy + "\n")
   
# Define electricity rates
D1_11 = Rate("D1_11", elctr_rates)
D1_2 = Rate("D1_2", elctr_rates)
D1_8 = Rate("D1_8", elctr_rates)

# Import hourly solar energy generation csv file created by NREL PV_Watts Calculator
df = pd.read_csv(solar_info['pvwatts_csv_path'], skiprows=31)

# Add three empty columns to the dataframe for each rate option: One to capture 
# electric sellback rate (¢/kWh) each hour, another to capture hourly profit ($) 
# if electricity is sold back, another to capture savings if electricity is used 
# (i.e. cost averted)
df["D1_11_sell_rate"] = np.nan
df["D1_11_profit"] = np.nan
df["D1_11_cost"] = np.nan
df["D1_2_sell_rate"] = np.nan
df["D1_2_profit"] = np.nan
df["D1_2_cost"] = np.nan
df["D1_8_sell_rate"] = np.nan
df["D1_8_profit"] = np.nan
df["D1_8_cost"] = np.nan

def calc_hourly_sellback_rate(rate):
    # Calculate the price of selling back electricity to the grid for each hour
    # of each day of the year
    if rate.name != 'D1_8':
        if (month < rate.smmr[0]) or (month > rate.smmr[1]):
            # winter
            if (hour < rate.peak[0]) or (hour > rate.peak[1]):
                # off peak
                df.iloc[
                    i, df.columns.get_loc(rate.name + "_sell_rate")
                ] = rate.wntr_offpk_sell
            else:
                # on peak
                df.iloc[
                    i, df.columns.get_loc(rate.name + "_sell_rate")
                ] = rate.wntr_peak_sell
        else:
            # summer
            if (hour < rate.peak[0]) or (hour > rate.peak[1]):
                # off peak
                df.iloc[
                    i, df.columns.get_loc(rate.name + "_sell_rate")
                ] = rate.smmr_offpk_sell
            else:
                # on peak
                df.iloc[
                    i, df.columns.get_loc(rate.name + "_sell_rate")
                ] = rate.smmr_peak_sell
    else:
            if (hour >= rate.peak[0]) and (hour < rate.peak[1]):
                # on peak
                df.iloc[
                    i, df.columns.get_loc(rate.name + "_sell_rate")
                ] = rate.offpk_sell
            if ((hour >= rate.mdpeak[0][0]) and (hour < rate.mdpeak[0][1]) or (hour >= rate.mdpeak[1][0]) and (hour < rate.mdpeak[1][1])):
                # mid peak
                 df.iloc[
                    i, df.columns.get_loc(rate.name + "_sell_rate")
                ] = rate.midpk_sell
            else:
                # off peak
                df.iloc[
                    i, df.columns.get_loc(rate.name + "_sell_rate")
                ] = rate.peak_sell

# Calculate the hourly electricity sellback rate for each rate option (i.e.
# D1.11 and D1.2)
for i in range(0, len(df.index)):
    hour = df.iloc[i][2]
    month = df.iloc[i][0]
    calc_hourly_sellback_rate(D1_11)
    calc_hourly_sellback_rate(D1_2)
    calc_hourly_sellback_rate(D1_8)

# Get the product of the hourly energy production in kWh and the hourly sellback
# rate in $/kWh
df["D1_11_profit"] = df["AC System Output (W)"] / 1000 * df["D1_11_sell_rate"] / 100
df["D1_2_profit"] = df["AC System Output (W)"] / 1000 * df["D1_2_sell_rate"] / 100
df["D1_8_profit"] = df["AC System Output (W)"] / 1000 * df["D1_8_sell_rate"] / 100
D1_11_profit = df["D1_11_profit"].sum()
D1_2_profit = df["D1_2_profit"].sum()
D1_8_profit = df["D1_8_profit"].sum()

# Get the product of the hourly energy production in kWh and the hourly purchase
# rate in $/kWh
df["D1_11_cost"] = (
    df["AC System Output (W)"] / 1000 * (df["D1_11_sell_rate"] + D1_11.distr) / 100
)
df["D1_2_cost"] = (
    df["AC System Output (W)"] / 1000 * (df["D1_2_sell_rate"] + D1_2.distr) / 100
)
df["D1_8_cost"] = (
    df["AC System Output (W)"] / 1000 * (df["D1_8_sell_rate"] + D1_8.distr) / 100
)
D1_11_value = df["D1_11_cost"].sum()
D1_2_value = df["D1_2_cost"].sum()
D1_8_value = df["D1_8_cost"].sum()

# Print the results
print("Annual profit selling all electricity back to DTE:")
print("\t D1_11: $" + "{:0,.2f}".format(D1_11_profit))
print("\t D1_02: $" + "{:0,.2f}".format(D1_2_profit))
print("\t D1_08: $" + "{:0,.2f}".format(D1_8_profit))

Cost = solar_info['cost']
print("\nPayback Period (years):")
print("\t D1_11: " + "{:0,.1f}".format(Cost / D1_11_profit))
print("\t D1_02: " + "{:0,.1f}".format(Cost / D1_2_profit))
print("\t D1_08: " + "{:0,.1f}".format(Cost / D1_8_profit))

print("\nAnnual savings selling zero electricity back to DTE:")
print("\t D1_11: $" + "{:0,.2f}".format(D1_11_value))
print("\t D1_02: $" + "{:0,.2f}".format(D1_2_value))
print("\t D1_08: $" + "{:0,.2f}".format(D1_8_value))

print("\nPayback Period (years):")
print("\t D1_11: " + "{:0,.1f}".format(Cost / D1_11_value))
print("\t D1_02: " + "{:0,.1f}".format(Cost / D1_2_value))
print("\t D1_08: " + "{:0,.1f}".format(Cost / D1_8_value))
