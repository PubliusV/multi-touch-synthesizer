import streamlit as st
import pandas as pd
import uuid
import random
from random import randrange
from datetime import datetime, timedelta
import time
import pickle
import numpy as np
from scipy.stats import poisson

########################
# function definitions #
########################

random.seed(9001)
np.random.seed(9001)

@st.cache_data # IMPORTANT: Cache the conversion to prevent computation on every rerun
def convert_df(df):
    return df.to_csv().encode('utf-8')

def synthesize_touchpoints(channel_stats, # a DF containing all the channel-level descriptive stats
                           unique_id_count,
                           touchpoint_lambda
                           ):
    # Create a pandas dataframe which we'll write our touchpoint data to
    touchpoint_df = pd.DataFrame(columns=['uid','touch_sequence','channel','conversion','monetary_value'])
    channel_list = channel_stats['channel']
    channel_relative_freq = channel_stats['channel_relative_freq']

    # Generate list of random user IDs
    uid_list = []
    for _ in range(unique_id_count):
        uid_list.append(str(uuid.uuid4()).replace('-',''))

    # Generate data / user journey for each unique user ID
    for uid in uid_list:
        num_touchpoints = poisson.rvs(mu=touchpoint_lambda, size=1)[0]
        cvr_list = []
        # Over each touchpoint...
        for i in range(num_touchpoints):
            # track the number of touchpoints, starting at one
            touch_seq = i+1


            # if we aren't on the last touchpoint yet...
            if i < (num_touchpoints-1):
                # randomly choose a channel, weighted by the relative frequency
                touchpoint_channel = random.choices(channel_list, channel_relative_freq, k=1)[0]
                touchpoint_cvr = channel_stats[channel_stats['channel']==touchpoint_channel]['channel_cvr'].values[0]
                cvr_list.append(touchpoint_cvr)
                # add it to the touchpoint dataframe
                touchpoint_df = pd.concat([pd.DataFrame([[uid,touch_seq,touchpoint_channel,0,0]], columns=touchpoint_df.columns), touchpoint_df], ignore_index=True)
            # on the last touchpoint
            else:
                # randomly choose a channel, weighted by the relative frequency
                touchpoint_channel = random.choices(channel_list, channel_relative_freq , k=1)[0]


                # pull the conversion stats and randomly decide if this user converts
                touchpoint_cvr = channel_stats[channel_stats['channel']==touchpoint_channel]['channel_cvr'].values[0]
                cvr_list.append(touchpoint_cvr)
                final_cvr = sum(cvr_list)
                conversion_flag = random.choices([0,1], (1-final_cvr, final_cvr), k=1)[0]
                # conversion_flag = max(cvr_list)

                if conversion_flag == 1:
                    # pull the conversion stats
                    touchpoint_aov = channel_stats[channel_stats['channel']==touchpoint_channel]['channel_aov']
                    touchpoint_stdev = channel_stats[channel_stats['channel']==touchpoint_channel]['channel_stdev']

                    # randomly select an order value from a normal distribution with the data above for shape
                    conversion_value = np.random.normal(touchpoint_aov,
                                                        touchpoint_stdev)[0]
                else:
                    conversion_value = 0

                touchpoint_df = pd.concat([pd.DataFrame([[uid,touch_seq,touchpoint_channel,conversion_flag,conversion_value]], columns=touchpoint_df.columns), touchpoint_df], ignore_index=True)  
    
    return touchpoint_df


##################
# Data Synthesis #
##################

# Set the default platform options, and their associated values
# The user can change these later.
platform_opts_df = pd.DataFrame(
    [
        {"channel":'Paid Social',"channel_cvr":0.02, "channel_relative_freq":.20,'channel_aov':95,'channel_stdev':5},
        {"channel":'Paid Search (Other)',"channel_cvr":0.02,"channel_relative_freq":.1,'channel_aov':90,'channel_stdev':10},
        {"channel":'Google Display Network',"channel_cvr":0.025,"channel_relative_freq":.30,'channel_aov':100,'channel_stdev':30},
        {"channel":'Affiliate',"channel_cvr":0.04,"channel_relative_freq":.30,'channel_aov':120,'channel_stdev':15},
        {"channel":'Email',"channel_cvr":0.05,"channel_relative_freq":.1,'channel_aov':130,'channel_stdev':5}
    ]
)

st.title("Generate Synthetic User Touchpoints")
st.divider()
st.subheader("High Level Simulation Parameters")
user_num_simulated_users = st.number_input("How many users would you like to simulate?",min_value=50, max_value=10000000,value=1000)
user_poisson_lambda = st.number_input("What is the average number of touchpoints over the interval you're simulating? (must be an integer)",value=10, step=1)

st.divider()
st.subheader("Channel Level Simulation Parameters")
st.write("Please Use the DataFrame Editor to Add or Modify Marketing Channels for Your Simulation:")
user_channel_opts = st.data_editor(platform_opts_df, num_rows="dynamic")

if st.button("Generate Simulated Data"):
    synthetic_touchpoints = synthesize_touchpoints(user_channel_opts, user_num_simulated_users, user_poisson_lambda)
    synthetic_touchpoints = synthetic_touchpoints.sort_values(by=['uid','touch_sequence'])

st.divider()

try:
    st.write(synthetic_touchpoints.head(20))

    csv = convert_df(synthetic_touchpoints)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name=f'synthetic_touchpoints_{str(time.time())}.csv',
        mime='text/csv'
    )
    st.download_button(
        label="Download data as PKL",
        data=pickle.dumps(synthetic_touchpoints),
        file_name=f'synthetic_touchpoints_{str(time.time())}.pkl',
    )

except:
    st.write("Generate data to see a preview and save.")

if 'synthetic_touchpoints' in locals():
    with open('synthetic_touchpoints.pkl', 'wb') as handle:
        pickle.dump(synthetic_touchpoints, handle)