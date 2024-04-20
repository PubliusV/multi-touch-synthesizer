import streamlit as st
import pandas as pd
import pickle
from ChannelAttribution import *
import plotly.io as pio
import plotly.graph_objects as go
import plotly.express as px
import locale

locale.setlocale( locale.LC_ALL, '' )

def user_journey_from_touchpoints(df):
    # Generate user-level journey table from touchpoint-level table
    # takes dataframe (with 'uid', 'conversion', and 'channel' headers)
    # returns dataframe with user id, journey, and whether the user converted
    journeys = df.groupby('uid')['channel'].apply(' > '.join).reset_index()
    conversions = df.groupby('uid')['conversion'].max()
    monetary = df.groupby('uid')['monetary_value'].max()

    return journeys.merge(conversions, on='uid').merge(monetary, on='uid')


with open('synthetic_touchpoints.pkl', 'rb') as handle:
    synth_data = pickle.load(handle)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric('Total Simulated Orders', synth_data['conversion'].sum())
with col2:
    st.metric('Total Simulated Revenue', locale.currency(round(synth_data['monetary_value'].sum(),2), grouping=True))
with col3:
    st.metric('Total Simulated Sessions', synth_data['uid'].count())

st.write("Please fill this table with CPC approximations if you would like to see ROAS estimates.")
spend_input_df = pd.DataFrame(synth_data['channel'].copy(deep=True).unique())
spend_input_df = spend_input_df.rename(columns={0:'channel_name'})
spend_input_df['channel_cpc'] = 3.0
channel_spend_data = st.data_editor(spend_input_df)

t1,t2,t3,t4 = st.tabs(["Conversions","Revenue","Conversion Rate","ROAS"])

user_journeys = user_journey_from_touchpoints(synth_data)

H = heuristic_models(user_journeys,"channel","conversion",var_value="monetary_value")
M = markov_model(user_journeys,"channel","conversion",var_value="monetary_value")

R = pd.merge(H,M,on="channel_name",how="inner")
R1 = R[["channel_name","first_touch_conversions","last_touch_conversions",\
"linear_touch_conversions","total_conversions"]]

R1.columns = ["channel_name","first_touch","last_touch","linear_touch","markov_model"]
R1 = pd.melt(R1, id_vars="channel_name")


R2=R[["channel_name","first_touch_value","last_touch_value",\
"linear_touch_value","total_conversion_value"]]
R2.columns=["channel_name","first_touch","last_touch","linear_touch","markov_model"]

R2=pd.melt(R2, id_vars="channel_name")

with t1:
    fig = px.bar(R1, x="channel_name", y="value", color="variable", barmode="group", title="Attributed Conversions by Channel and Attribution Model")
    fig.update_xaxes(title_text="Attribution Channel")
    fig.update_yaxes(title_text="Attributed Conversions")
    st.plotly_chart(fig)

with t2:
    fig2 = px.bar(R2, x="channel_name", y="value", color="variable", barmode="group", title="Attributed Revenue by Channel and Attribution Model")
    fig2.update_xaxes(title_text="Attribution Channel")
    fig2.update_yaxes(title_text="Attributed Revenue")
    st.plotly_chart(fig2)

channel_sessions = synth_data.groupby('channel')['uid'].count().reset_index()
channel_sessions.rename(columns = {"uid":"sessions","channel":"channel_name"},inplace=True)

combined_models = H.merge(M, on='channel_name').merge(channel_sessions, on='channel_name').merge(channel_spend_data,on='channel_name')
models=["first_touch","last_touch","linear_touch","markov_model"]
combined_models['total_cost'] = combined_models['sessions']*combined_models['channel_cpc']

i=0
for col in combined_models[['first_touch_conversions','last_touch_conversions','linear_touch_conversions','total_conversions']]:
    combined_models[models[i]+'_CVR'] = combined_models[col]/combined_models['sessions']
    i+=1

i=0
for col in combined_models[['first_touch_value','last_touch_value','linear_touch_value','total_conversion_value']]:
    combined_models[models[i]+'_ROAS'] = combined_models[col]/combined_models['total_cost']
    i+=1

with t3:

    R3=combined_models[["channel_name","first_touch_CVR","last_touch_CVR",\
    "linear_touch_CVR","markov_model_CVR"]]
    R3.columns=["channel_name","first_touch","last_touch","linear_touch","markov_model"]

    R3=pd.melt(R3, id_vars="channel_name")

    fig3 = px.bar(R3, x="channel_name", y="value", color="variable", barmode="group", title="Attributed Conversion Rate by Channel and Attribution Model")
    fig3.update_xaxes(title_text="Attribution Channel")
    fig3.update_yaxes(title_text="Attributed CVR")
    st.plotly_chart(fig3)

with t4:
    R4=combined_models[["channel_name","first_touch_ROAS","last_touch_ROAS",\
    "linear_touch_ROAS","markov_model_ROAS"]]
    R4.columns=["channel_name","first_touch","last_touch","linear_touch","markov_model"]

    R4=pd.melt(R4, id_vars="channel_name")

    fig4 = px.bar(R4, x="channel_name", y="value", color="variable", barmode="group", title="Attributed ROAS by Channel and Attribution Model")
    fig4.update_xaxes(title_text="Attribution Channel")
    fig4.update_yaxes(title_text="Attributed ROAS")
    st.plotly_chart(fig4)

combined_models = combined_models.rename(columns={"total_conversions":"markov_model_conversions","total_conversion_value":"markov_model_value"})
st.write(combined_models)

