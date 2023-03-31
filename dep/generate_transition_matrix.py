#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 12:42:14 2022

@author: jrdonoso
"""
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import seaborn as sns

# Data exploration
#df3=all_data.groupby(['time_of_day','location']).count()

#day = 'monday'
def adjust_day_data(day_data):
    day_data.index = pd.to_datetime(day_data.index)
    customer_df = []
    for customer_no in day_data.customer_no.unique():
        # Current customer DataFrame
        curr_cust_df = day_data[day_data.customer_no == customer_no].sort_index()
        entrance = pd.DataFrame({
            'timestamp': [curr_cust_df.index[0]-pd.Timedelta(minutes=1)],
            'customer_no':[customer_no],
            'location':['entrance']}).set_index('timestamp')
        curr_cust_df = curr_cust_df.append(entrance).sort_index()
        #
        if curr_cust_df.iloc[-1].location!='checkout':
            print(f"Missing checkout detected in customer {customer_no}...")
            checkout = pd.DataFrame({
                'timestamp': [curr_cust_df.index[-1]+pd.Timedelta(minutes=2)],
                'customer_no':[customer_no],
                'location':['checkout']}).set_index('timestamp')
            curr_cust_df = curr_cust_df.append(checkout)
            
        customer_df.append(curr_cust_df)
    return pd.concat(customer_df)

def add_staying_minutes(df_):
    """
    Fill in missing minutes in DataFrame table df_ containing timestamp, 
    customer_no and customer location
    """
    df = df_.copy()
    df = df.reset_index() #add integer indices 
    last_timestamp = df.iloc[-1].timestamp
    k = 0
    while df.iloc[k].timestamp < last_timestamp:
        curr_location = df.iloc[k].location
        curr_cust = df.iloc[k].customer_no
        if curr_location!='checkout': #exclude checkout rows
            curr_timestamp = df.iloc[k].timestamp
            time_dif = df.iloc[k+1].timestamp - curr_timestamp #Time difference between rows
            if time_dif.seconds > 60: 
                # Insert row between current and next
                df.loc[(2*k+1)/2]= curr_timestamp + pd.Timedelta(minutes=1),curr_cust,curr_location#,curr_location
                df = df.sort_index().reset_index(drop=True)
        k = k+1
    return df
                
days_df = []
for day in ['monday','tuesday','wednesday','thursday','friday']:
    print(f"Processing {day}.....")
    day_data = pd.read_csv(f"./data/{day}.csv",';',index_col=0)
    days_df.append(adjust_day_data(day_data))

all_data = pd.concat(days_df)
#test_data = all_data.copy()
all_data = add_staying_minutes(all_data)
all_data['next_location']=all_data.location.shift(-1)
all_data['day_of_week']=all_data.index.day_of_week+1

# Set next state after checkout
all_data.loc[all_data.location=='checkout','next_location']='checkout'

#all_data['time_of_day']=all_data.index.time
#times=all_data[all_data.day_of_week==1][['time_of_day','location']]
#ent_time=times[times.location=='entrance'].groupby('time_of_day').count()


# Create transition matrix
P = pd.crosstab(
    all_data['location'], 
    all_data['next_location'], normalize='index')

# Add missing entrance column
P.insert(3, 'entrance', [0,0,0,0,0,0])
# Convert transition matrix to dictionary
#probs = P.to_dict(orient='index')
sns.heatmap(P,annot=True)
