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
    return pd.melt(yield_ca.reset_index(), id_vars=['date'], var_name='Maturity', value_name='Bond Yield')

yield_ca = get_data()
dates = sorted(yield_ca['date'].unique())

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

df = yield_ca[(yield_ca['date'] == min) | (yield_ca['date'] == max)]
df['date'] = df['date'].dt.strftime('%Y-%m-%d')

st.title('Yield Curve')

curve = alt.Chart(df).mark_line().encode(
    x='Maturity',
    y='Bond Yield',
    color=alt.Color('date', scale=alt.Scale(domain=[df['date'].iloc[1], df['date'].iloc[0]]), legend=alt.Legend(title='Dates', orient='top'))
)

history = alt.Chart(yield_ca[yield_ca['date'].between(min, max)]).mark_line().encode(
    x='date',
    y='Bond Yield',
    color='Maturity'
)

st.altair_chart(curve & history)