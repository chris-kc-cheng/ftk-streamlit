import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
import toolkit as ftk

@st.cache_data(ttl=3600)
def get_data() -> pd.DataFrame:
    m = 120  # Periods
    n = 10  # Categories
    df = pd.DataFrame(
        np.random.randn(m, n) / 10,
        index=pd.period_range(end=pd.Timestamp.today(), periods=m, freq='M'),
        columns=[f'Cat. {chr(65 + x)}' for x in range(n)]
    )
    df.index.name = 'Date'
    df.columns.name = 'Category'
    return df

data = get_data()

with st.sidebar:
    pass

st.title('Performance and Risk Analysis')

row1 = st.columns(3)

for col in row1:
    card = col.container(border=True, vertical_alignment='center', height='stretch')
    card.write(123)