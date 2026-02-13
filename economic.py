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
        st.warning('Unable to fetch US data')  # API daily limit

    df = pd.concat({
        ('Canada', 'CPI'): ca[41690973].ffill().pct_change(12).dropna(),
        ('Canada', 'Unemployment'): ca[2062815] / 100,
        ('US', 'CPI'): us['CUUR0000SA0'].ffill().pct_change(12).dropna() if not us.empty else pd.Series(),
        ('US', 'Unemployment'): us['LNS14000000'] / 100
    })
    df.name = 'Value'
    df.index.names = ['Country', 'Indicator', 'Date']
    return df.reset_index()


data = get_data()

with st.sidebar:
    st.markdown('')

st.title('Economic Indicators')

indicators = data['Indicator'].unique().tolist()
countries = data['Country'].unique()
tabs = st.tabs(indicators)

for i, tab in enumerate(tabs):

    indicator = indicators[i]

    row = tab.columns(len(countries))
    for j, col in enumerate(row):
        country = countries[j]
        with col.container(border=True, horizontal_alignment='center'):
            df = data[(data['Country'] == country) &
                      (data['Indicator'] == indicator)]
            s = df['Value']
            st.metric(country, s.iloc[-1], s.iloc[-1] - s.iloc[-2], help=str(
                df['Date'].iloc[-1]), format='percent', delta_color='inverse')

    tab.altair_chart(
        alt.Chart(data).transform_filter(
            alt.datum.Indicator == indicator
        ).mark_line().encode(
            x='Date',
            y=alt.Y('Value', axis=alt.Axis(format='%', title=indicator)),
            color='Country'
        )
    )
