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

        case 'Hedge Fund Indexes':
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

        case _:
            pass

    return df


category = 'Zero'

with st.sidebar:

    dataset = st.selectbox(
        'Data', ['Asset Classes', 'Hedge Fund Indexes', 'Random'], 0)
    raw = get_data(dataset)
    data = raw.copy()

    freq = st.segmented_control(
        'Period', ['Monthly', 'Quarterly', 'Annually'], default=['Annually'])

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

# Aggregate
freq_options = {
    'Monthly': ('ME', '%Y-%m'),
    'Quarterly': ('QE', '%Y Q%q'),
    'Annually': ('YE', '%Y')
}
data = data.groupby(pd.Grouper(freq='YE' if freq is None else freq_options[freq][0])).apply(
    lambda r: np.expm1(np.log1p(r).sum()))

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
data['Date'] = data['Date'].dt.strftime(
    '%Y' if freq is None else freq_options[freq][1])

height = (data['Rank'].max() - data['Rank'].min()) * 30 + 150
width = data['Date'].nunique() * 60 + 100

rng = max(abs(data['Return'].max()), abs(data['Return'].min()))
scale = alt.Scale(
    domain=[-rng, 0, rng],
    range=['red', '#fefefe', 'green']
)

st.title('Periodic Table')

base = alt.Chart(data)
heatmap = base.mark_rect().encode(
    x="Date:N",
    y=alt.Y('Rank:O', sort='descending', axis=None),
    color=alt.Color('Return:Q', scale=scale, title='Return', legend=alt.Legend(
        format='.0%')) if color == 'Return' else alt.Color('Category:N', title='Category'),
).properties(
    height=height,
    width=width
)
text1 = base.mark_text(dy=-7, fontWeight='bold').encode(
    x='Date:N',
    y=alt.Y('Rank:O', sort='descending', axis=None),
    text='Category:N'
)
text2 = base.mark_text(dy=7).encode(
    x='Date:N',
    y=alt.Y('Rank:O', sort='descending', axis=None),
    text='Percent:N'
)
chart = heatmap + text1 + text2
st.altair_chart(chart, width='content')

with st.expander('Data', expanded=False):
    st.write(raw.style.format("{:.2%}"))
