import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
import toolkit as ftk


@st.cache_data(ttl=3600)
def get_data(dataset: str) -> pd.DataFrame:
    """Load a dataset

    Parameters
    ----------
    dataset : str
        Name of the dataset

    Returns
    -------
    pd.DataFrame
        Index is a PeriodIndex named `Date`
        Column name is `Category`
    """

    m = 120  # Periods
    n = 10  # Categories
    df = pd.DataFrame(
        np.random.randn(m, n) / 10,
        index=pd.period_range(end=pd.Timestamp.today(), periods=m, freq='M'),
        columns=[f'Cat. {chr(65 + x)}' for x in range(n)]
    )
    df.index.name = 'Date'
    df.columns.name = 'Category'

    desc = 'Normally distributed random returns generated for testing purpose.'

    match dataset:
        case 'Asset Classes':
            tickers = {
                'CSUS.L': 'US Eq.',
                'IEUR': 'Europe Eq.',
                'EWJ': 'Japan Eq.',
                'MCHI': 'China Eq.',
                'EEM': 'EM Eq.',
                'IGLO.L': 'Gov',
                'EMB': 'EMD',
                'CRPA.L': 'IG',
                'GHYG': 'HY',
                '^SPGSCI': 'Cmdty',
                'REET': 'REITs',
                'IGF': 'Infra',
                'IBTU.L': 'Cash'
            }
            df = ftk.get_yahoo_bulk(tickers.keys()).groupby(
                pd.Grouper(freq='ME')).last().pct_change().dropna()
            df = df.rename(columns=tickers)
            df.index = df.index.to_period('M')
            df.columns.name = 'Category'

            desc = 'The performance of major asset classes, represented using ETFs as proxies.'

        case 'MSCI ACWI Sectors':
            sectors = {
                892400: 'ACWI',
                106745: 'Energy',
                106747: 'Industrials',
                106746: 'Materials',
                106749: 'Con. Stap.',
                106748: 'Con. Disc.',
                106751: 'Financials',
                106750: 'Health',
                106753: 'Comm',
                106752: 'Tech',
                106754: 'Util',
                132082: 'R/E'
            }
            df = ftk.get_msci(sectors.keys(), variant='GRTR').dropna()
            df.columns = sectors.values()
            df.columns.name = 'Category'

            desc = 'Returns for all 11 MSCI ACWI sectors.'

        case 'MSCI ACWI Factors':
            factors = {
                892400: 'ACWI',
                700404: 'Volatility',
                701633: 'Yield',
                702786: 'Quality',
                703026: 'Momentum',
                706767: 'Value',
                129859: 'Size',
                729745: 'Growth'
            }
            df = ftk.get_msci(factors.keys(), variant='GRTR').dropna()
            df.columns = factors.values()
            df.columns.name = 'Category'

            desc = 'Returns for the major MSCI ACWI factors.'

        case 'Hedge Fund - Asia':
            df = ftk.get_withintelligence_bulk(
                [11425, 11449, 11431, 11451, 11454, 11453, 11450, 11430, 11443, 11452])
            df = df.rename(columns={
                'With Intelligence Asia Equity Hedge Fund Index': 'Equity',
                'With Intelligence Asia Event Driven Hedge Fund Index': 'Event',
                'With Intelligence Asia Fund of Funds Index': 'FoF',
                'With Intelligence Asia Long/Short Equity Hedge Fund Index': 'L/S',
                'With Intelligence Asia Hedge Fund Index': 'HF',
                'With Intelligence Asia Relative Value Hedge Fund Index': 'RV',
                'With Intelligence Asia Fixed Income/Credit Hedge Fund Index': 'FI/Credit',
                'With Intelligence Asia Macro Hedge Fund Index': 'Macro',
                'With Intelligence Asia Asset Weighted Index - USD': 'Asset Wtg.',
                'With Intelligence Asia Multi-Strategy Hedge Fund Index': 'Multi'
            })
            df.index.name = 'Date'
            df.columns.name = 'Category'
            # Fix data issues - missing or duplicated returns
            df = df.dropna()
            df = df[~df.index.duplicated(keep='first')]

            desc = 'Main strategy returns from the WithIntelligence Hedge Fund Index.'            

        case 'Hedge Fund - Global':
            df = ftk.get_withintelligence_bulk(
                [11469, 11475, 11470, 11471, 11420, 11473, 11474, 11454, 11486])
            df = df.rename(columns={
                'With Intelligence Hedge Fund Index': 'HF',
                'With Intelligence Relative Value Hedge Fund Index': 'RV',
                'With Intelligence CTA Index': 'CTA',
                'With Intelligence Event Driven Hedge Fund Index': 'Event',
                'With Intelligence Long/Short Equity Hedge Fund Index': 'L/S',
                'With Intelligence Macro Hedge Fund Index': 'Macro',
                'With Intelligence Multi-Strategy Hedge Fund Index': 'Multi',
                'With Intelligence Asia Hedge Fund Index': 'Asia',
                'With Intelligence 50': 'Top 50'
            })
            df.index.name = 'Date'
            df.columns.name = 'Category'
            # Fix data issues - missing or duplicated returns
            df = df.dropna()
            df = df[~df.index.duplicated(keep='first')]

            desc = 'Main strategy returns from the WithIntelligence Hedge Fund Index.'

        case _:
            pass

    return df, desc


category = 'Zero'

with st.sidebar:

    dataset = st.selectbox(
        'Data', ['Asset Classes', 'MSCI ACWI Sectors', 'MSCI ACWI Factors', 'Hedge Fund - Asia', 'Hedge Fund - Global', 'Random'], 0)
    raw, desc = get_data(dataset)
    data = raw.copy()

    freq = st.segmented_control(
        'Period', ['Monthly', 'Quarterly', 'Annually', 'Trailing'], default=['Annually'])

    categories = ['Zero']
    categories.extend(data.columns)
    display = st.segmented_control(
        'Rank', ['Absolute', 'Relative'], default='Absolute')
    if display == 'Relative':
        category = st.selectbox('Relative to', categories, 0)
    color = st.segmented_control(
        'Color by', ['Return', 'Category'], default='Return')
    decimal = st.segmented_control('Decimal places', [0, 1, 2], default=1)
    if decimal is None:
        decimal = 0
    annualize = st.toggle('Annualize', value=True)

# Aggregate
freq_options = {
    'Monthly': ('ME', '%Y-%m'),
    'Quarterly': ('QE', '%Y Q%q'),
    'Annually': ('YE', '%Y')
}

horizons = {
    '1 Mo': 1,
    '3 Mo': 3,
    '6 Mo': 6,
    '1 Yr': 12,
    '2 Yr': 24,
    '3 Yr': 36,
    '4 Yr': 48,
    '5 Yr': 60,
    '6 Yr': 72,
    '7 Yr': 84,
    '8 Yr': 96,
    '9 Yr': 108,
    '10 Yr': 120
}

if freq in freq_options:
    data = data.groupby(pd.Grouper(freq=freq_options[freq][0])).apply(
        lambda r: np.expm1(np.log1p(r).sum()))
else:
    data = pd.DataFrame({
        horizon: np.expm1(np.log1p(data.tail(months)).sum()
                          * 12 / (months if annualize and months > 12 else 12))
        for horizon, months in horizons.items() if len(data) >= months
    }).T
    data.index.name = 'Date'

# Reshape to long format
data = data.stack().to_frame('Return')
data['Percent'] = data['Return'].map(f"{{:.{decimal}%}}".format)

# Reference asset
ref = data[data.index.get_level_values(1) == category][['Return']].rename(
    columns={'Return': 'Ref'}
).droplevel(1)

if category == 'Zero':
    data['Ref'] = 0
else:
    data = data.join(ref, how='left')
data['Rel'] = data['Return'] - data['Ref']

# Rank
data['Rank'] = np.nan
pos = data['Rel'] >= 0
neg = data['Rel'] < 0
if display == 'Absolute':
    data['Rank'] = data.groupby('Date')['Return'].rank(
        ascending=True, method='dense')
else:
    data.loc[pos, 'Rank'] = data[pos].groupby(
        'Date')['Rel'].rank(ascending=True, method='dense')
    data.loc[neg, 'Rank'] = - \
        data[neg].groupby('Date')['Rel'].rank(ascending=False, method='dense')
data = data.reset_index()
if freq in freq_options:
    data['Date'] = data['Date'].dt.strftime(freq_options[freq][1])
else:
    data['Months'] = data['Date'].map(horizons)

# Chart Formatting
height = (data['Rank'].max() - data['Rank'].min()) * 30 + 150
width = data['Date'].nunique() * 60 + 100
rng = max(abs(data['Return'].max()), abs(data['Return'].min()))
scale = alt.Scale(
    domain=[-rng, 0, rng],
    range=['red', '#fefefe', 'green']
)

st.title('Periodic Table')
st.markdown(f'### {dataset}')
st.markdown(desc)

# Chart
base = alt.Chart(data)
xaxis = alt.X('Date:N', axis=alt.Axis(title=None)) if freq in freq_options else alt.X('Date', axis=alt.Axis(title=None), sort=alt.SortField('Months:O', order='ascending'))
heatmap = base.mark_rect().encode(
    x=xaxis,
    y=alt.Y('Rank:O', axis=None, sort='descending'),
    color=alt.Color('Return:Q', scale=scale, title='Return', legend=alt.Legend(
        format='.0%')) if color == 'Return' else alt.Color('Category:N', title='Category'),
).properties(
    height=height,
    width=width
)
text1 = base.mark_text(dy=-7, fontWeight='bold').encode(
    x=xaxis,
    y=alt.Y('Rank:O', sort='descending', axis=None),
    text='Category:N'
)
text2 = base.mark_text(dy=7).encode(
    x=xaxis,
    y=alt.Y('Rank:O', sort='descending', axis=None),
    text='Percent:N'
)
chart = heatmap + text1 + text2
st.altair_chart(chart, width='content')
st.write('Data as of:', raw.index[-1])

with st.expander('Data', expanded=False):
    st.write(raw.style.format("{:.2%}"))
