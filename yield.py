import pandas as pd
import streamlit as st
import altair as alt
import toolkit as ftk

import requests
from io import BytesIO
from zipfile import ZipFile

fields = {
    'FREQ:Frequency': 'freq',
    'REF_AREA:Reference area': 'country',
    'TIME_PERIOD:Time period or range': 'date',
    'OBS_VALUE:Observation Value': 'rate'
}

countries = ['CA', 'CH', 'CN', 'DE', 'FR', 'GB', 'HK',
             'IN', 'IT', 'JP', 'KR', 'MX', 'AU', 'US', 'XM']


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
        pd.melt(yield_ca.reset_index(), id_vars=['date'], var_name='Maturity', value_name='Bond Yield').assign(
            Region='Canada').rename(columns={'date': 'Date'}),
        pd.melt(yield_us.reset_index(), id_vars=['Date'], var_name='Maturity', value_name='Bond Yield').assign(Region='US')],
        ignore_index=True).dropna()


@st.cache_data(ttl=3600)
def get_policy():
    url = 'https://data.bis.org/static/bulk/WS_CBPOL_csv_flat.zip'
    response = requests.get(url)
    bytes = BytesIO(response.content)
    with ZipFile(bytes) as z:
        with z.open(z.namelist()[0]) as f:
            df = pd.read_csv(f)

    df = df.rename(columns=fields)
    df = df[df['freq'] == 'D: Daily'].drop(columns='freq')
    df[['iso', 'country']] = df['country'].str.split(':', expand=True)
    df = df[df['iso'].isin(countries)]
    df["date"] = pd.to_datetime(df["date"])
    df['rate'] = df['rate'].div(100)
    df = df[df['date'] >= '2020']

    return df


yc = get_data()
dates = sorted(yc['Date'].unique())
regions = sorted(yc['Region'].unique())

policy = get_policy()

with st.sidebar:

    min, max = st.select_slider(
        'Date range',
        options=dates,
        value=(
            dates[0],
            dates[-1]
        ),
        format_func=lambda d: d.strftime('%Y-%m-%d')
    )

df = yc[(yc['Date'] == min) | (yc['Date'] == max)]

st.title('Fixed Income Dashboard')

tab1, tab2 = st.tabs(['Canada & US Yield Curve', 'World Policy Rates'])
with tab1:

    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    curve = alt.Chart(df).mark_line().encode(
        x=alt.X('Maturity', title='Maturity (Years)'),
        y=alt.Y('Bond Yield', title='Bond Yield (%)'),
        color=alt.Color('Date', scale=alt.Scale(domain=[
                        df['Date'].iloc[1], df['Date'].iloc[0]]), legend=alt.Legend(title='Dates', orient='top'))
    ).facet(column=alt.Column('Region:N', header=alt.Header(title=None)))

    history = alt.Chart(yc[yc['Date'].between(min, max)]).mark_line().encode(
        x='Date',
        y=alt.Y('Bond Yield', title='Bond Yield (%)'),
        color=alt.Color('Maturity', title='Maturity (Years)',
                        legend=alt.Legend(orient='bottom'))
    ).facet(column=alt.Column('Region:N', header=alt.Header(title=None)))

    st.altair_chart(curve)
    st.altair_chart(history)

with tab2:
    policy = get_policy().fillna(method='ffill')

    scale = alt.Scale(domain=[policy['rate'].min(), policy['rate'].max()])
    line = alt.Chart(policy).mark_line().encode(
        x=alt.Y('date:T', title='Date'),
        y=alt.Y('rate:Q', title='Policy Rate',
                axis=alt.Axis(format='%'), scale=scale),
        color='country:N'
    ).properties(title='Historical')

    line_chart = line

    idx = policy.groupby('iso')['date'].idxmax()
    latest = policy.loc[idx].reset_index(drop=True)

    bar_chart = alt.Chart(latest).mark_bar().encode(
        x=alt.X('iso:N', title='Country', sort=alt.SortField(
            'rate', order='ascending')),
        y=alt.Y('rate:Q', title='Policy Rate',
                axis=alt.Axis(format='%'), scale=scale),
        color=alt.Color('country:N', title=None)
    ).properties(title='Latest')

    st.altair_chart(line_chart | bar_chart)
