import streamlit as st
import altair as alt
import numpy as np
import pandas as pd

# Data
@st.cache_data(ttl=3600)
def get_data():
    df = pd.DataFrame(
        np.random.randn(6, 4) / 10,
        index=[2021, 2022, 2023, 2024, 2025, 2026],
        columns=['Equity', 'Fixed Income', 'Hedge Fund', 'CTA']
    )
    df.index.name = 'Date'
    df.columns.name = 'Category'
    return df

data = get_data()

with st.sidebar:
    display = st.segmented_control('Display', ['Stacked', 'Relative to zero'], default='Stacked')
    color = st.segmented_control('Color by', ['Return', 'Category'], default='Return')
    decimal = st.segmented_control('Decimal places', [0, 1, 2], default=1)
    if decimal is None:
        decimal = 0

# Aggregate and reshape
data = data.groupby('Date').apply(lambda r: np.expm1(np.log1p(r).sum()))
data = data.stack().to_frame('Return')
data['Percent'] = data['Return'].map(f"{{:.{decimal}%}}".format)

# Rank
data['Rank'] = np.nan
pos = data['Return'] > 0
neg = data['Return'] < 0
if display == 'Stacked':
    data['Rank'] = data.groupby('Date')['Return'].rank(ascending=True, method='dense')
else:
    data.loc[pos, 'Rank'] = data[pos].groupby('Date')['Return'].rank(ascending=True, method='dense')
    data.loc[neg, 'Rank'] = -data[neg].groupby('Date')['Return'].rank(ascending=False, method='dense')
data = data.reset_index()
height = (data['Rank'].max() - data['Rank'].min()) * 30 + 150

scale = alt.Scale(
    domain=[-0.25, 0, 0.25],
    range=['red', 'white', 'green']
)


st.title('Asset Return Map')
st.write(display)
st.write(height)

base = alt.Chart(data)
heatmap  = base.mark_rect().encode(
    x="Date:N",
    y=alt.Y('Rank:O', sort='descending', axis=None),
    color=alt.Color('Return:Q', scale=scale, title='Return', legend=alt.Legend(format='.0%')) if color == 'Return' else alt.Color('Category:N', title='Category'),
).properties(
    height=height
)
text1 = base.mark_text(dy=-7).encode(
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
chart

st.dataframe(data)