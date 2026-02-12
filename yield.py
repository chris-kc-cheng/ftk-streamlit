import pandas as pd
import streamlit as st
import altair as alt
import toolkit as ftk

@st.cache_data(ttl=3600)
def get_data():    
    yield_ca = ftk.get_boc_bulk(['V80691342', 'V80691344', 'V80691345', 'V80691346', 'BD.CDN.2YR.DQ.YLD', 'BD.CDN.3YR.DQ.YLD', 'BD.CDN.5YR.DQ.YLD', 'BD.CDN.7YR.DQ.YLD', 'BD.CDN.10YR.DQ.YLD', 'BD.CDN.LONG.DQ.YLD'])\
                .groupby(pd.Grouper(freq='ME')).last()
    yield_ca.rename(columns={
        'V80691342': 1/12,
        'V80691344': 3/12,
        'V80691345': 6/12,
        'V80691346': 1,
        'BD.CDN.2YR.DQ.YLD': 2,
        'BD.CDN.3YR.DQ.YLD': 3,
        'BD.CDN.5YR.DQ.YLD': 5,
        'BD.CDN.7YR.DQ.YLD': 7,
        'BD.CDN.10YR.DQ.YLD': 10,
        'BD.CDN.LONG.DQ.YLD': 25}, inplace=True)
    
    yield_us = ftk.get_us_yield_curve(n=3)\
        .groupby(pd.Grouper(freq='ME')).last()
    yield_us.rename(columns={
        '1 Mo': 1/12,
        '1.5 Month': 1.5/12,
        '2 Mo': 2/12,
        '3 Mo': 3/12,
        '4 Mo': 4/12,
        '6 Mo': 6/12,
        '1 Yr': 1,
        '2 Yr': 2,
        '3 Yr': 3,
        '5 Yr': 5,
        '7 Yr': 7,
        '10 Yr': 10,
        '20 Yr': 20,
        '30 Yr': 30}, inplace=True)

    return pd.concat([
                pd.melt(yield_ca.reset_index(), id_vars=['date'], var_name='Maturity', value_name='Bond Yield').assign(Region='Canada').rename(columns={'date': 'Date'}),
                pd.melt(yield_us.reset_index(), id_vars=['Date'], var_name='Maturity', value_name='Bond Yield').assign(Region='US')],
                ignore_index=True).dropna()
                      

yc = get_data()
dates = sorted(yc['Date'].unique())
regions = sorted(yc['Region'].unique())

with st.sidebar:

    min, max = st.select_slider(
        'Date range',
        options=dates,
        value = (
            dates[0],
            dates[-1]
        ),
        format_func=lambda d: d.strftime('%Y-%m-%d')
    )

df = yc[(yc['Date'] == min) | (yc['Date'] == max)]

st.title('Yield Curve')

tabs = st.tabs(regions)
for i, region in enumerate(regions):
    with tabs[i]:

        df1 = df[df['Region'] == region]

        df1['Date'] = df1['Date'].dt.strftime('%Y-%m-%d')
        curve = alt.Chart(df1).mark_line().encode(
            x=alt.X('Maturity', title='Maturity (Years)'),
            y=alt.Y('Bond Yield', title='Bond Yield (%)'),
            color=alt.Color('Date', scale=alt.Scale(domain=[df1['Date'].iloc[1], df1['Date'].iloc[0]]), legend=alt.Legend(title='Dates', orient='top'))
        )

        history = alt.Chart(yc[(yc['Date'].between(min, max)) & (yc['Region'] == region)]).mark_line().encode(
            x='Date',
            y=alt.Y('Bond Yield', title='Bond Yield (%)'),
            color=alt.Color('Maturity', title='Maturity (Years)', legend=alt.Legend(orient='bottom'))
        )

        st.altair_chart(curve & history)