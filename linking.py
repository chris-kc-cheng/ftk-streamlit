import numpy as np
import pandas as pd
import streamlit as st
import toolkit as ftk


def total(source: pd.DataFrame, sum: bool = False, value: float = None) -> pd.DataFrame:
    df = source.copy()
    df['Total'] = df.sum(axis=1)
    if sum:
        df.loc['Total'] = df.sum(axis=0)
    elif value is None:
        df.loc['Total', 'Total'] = np.expm1(np.log1p(df['Total']).sum(axis=0))
    else:
        df.loc['Total', 'Total'] = value
    return df.style.format('{:.2%}')


st.title('Multi-Period Linking')
edit = st.toggle('Edit', value=False)

with st.sidebar:

    data = st.segmented_control(
        'Data', ['Sample 1', 'Sample 2'], default='Sample 1')

    p0 = pd.DataFrame()
    b0 = pd.DataFrame()

    if data == 'Sample 1':
        p0 = pd.DataFrame({
            'Sector 1': [-0.06, 0.04, 0.04, 0.04],
            'Sector 2': [0.02, -0.12, -0.02, 0.06],
            'Sector 3': [-0.12, 0.04, 0.21, 0.06]
        }, index=['Q1', 'Q2', 'Q3', 'Q4'])
        b0 = pd.DataFrame({
            'Sector 1': [0, 0.03, -0.06, 0.08],
            'Sector 2': [0.04, 0, -0.04, 0.06],
            'Sector 3': [0.14, 0, -0.1, 0]
        }, index=['Q1', 'Q2', 'Q3', 'Q4'])
    else:
        p0 = pd.DataFrame({
            'Allocation': [0.10, 0.08, 0.05, 0.10],
            'Selection':  [0.11, 0.06, 0.15, 0.07],
        }, index=['Q1', 'Q2', 'Q3', 'Q4'])
        b0 = pd.DataFrame({
            'Allocation': [0.04, 0.06, 0.04, 0.05],
            'Selection':  [0.07, 0.03, 0.08, 0.05],
        }, index=['Q1', 'Q2', 'Q3', 'Q4'])

col1, col2 = st.columns(2)
col1.markdown('#### Portfolio')

p = p0
b = b0

if edit:
    p = col1.data_editor(p0, num_rows='dynamic')
    p.index.name = 'Date'
else:
    col1.dataframe(total(p))

col2.markdown('#### Benchmark')
if edit:
    b = col2.data_editor(b0, num_rows='dynamic')
    b.index.name = 'Date'
else:
    col2.dataframe(total(b))

st.markdown('#### Active Return')
active = p - b

tabs = st.tabs(['Unadjusted', 'Carino Smoothing', 'Frongello',
               'Reversed Frongello', 'Modified Frongello'])
tabs[0].dataframe(total(active, value=np.expm1(np.log1p(p.sum(axis=1)).sum()
                                               ) - np.expm1(np.log1p(b.sum(axis=1)).sum())))
tabs[1].dataframe(total(ftk.carino(p, b), sum=True))
tabs[2].dataframe(total(ftk.frongello(p, b), sum=True))
tabs[3].dataframe(total(ftk.frongello(p, b, sel=0), sum=True))
tabs[4].dataframe(total(ftk.frongello(p, b, sel=0.5), sum=True))
