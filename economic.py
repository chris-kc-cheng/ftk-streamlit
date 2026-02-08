import pandas as pd
import streamlit as st
import altair as alt
import toolkit as ftk

@st.cache_data(ttl=3600)
def get_data():    
    
    ca = ftk.get_statcan_bulk(n=120)
    us = pd.DataFrame(columns=['CUUR0000SA0', 'LNS14000000'])
    try:
        us = ftk.get_bls_bulk()
    except Exception as e:
        st.warning('Unable to fetch US data')

    df = pd.concat({
        ('Canada', 'CPI'): ca[41690973].pct_change(12).dropna(),
        ('Canada', 'Unemployment'): ca[2062815] / 100,        
        ('US', 'CPI'): us['CUUR0000SA0'].pct_change(12).dropna() if not us.empty else pd.Series(),
        ('US', 'Unemployment'): us['LNS14000000'] / 100
    })
    df.name = 'Value'
    df.index.names = ['Country', 'Indicator', 'Date']
    return df.reset_index()

data = get_data()

st.title('Economic Indicators')

st.altair_chart(
    alt.Chart(data).transform_filter(
        alt.datum.Indicator == 'CPI'
    ).mark_line().encode(
        x='Date',
        y = alt.Y('Value', axis=alt.Axis(format='%', title='CPI YoY')),
        color='Country'
    )
)

st.altair_chart(
    alt.Chart(data).transform_filter(
        alt.datum.Indicator == 'Unemployment'
    ).mark_line().encode(
        x='Date',
        y = alt.Y('Value', axis=alt.Axis(format='%', title='Unemployment Rate')),
        color='Country'
    )
)
