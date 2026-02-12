import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
import toolkit as ftk

@st.cache_data(ttl=3600)
def get_data() -> pd.DataFrame:
    data = pd.read_csv('data/test.csv', index_col=0)
    data.index = pd.PeriodIndex(data.index, freq='M')
    return data

with st.sidebar:
    text = st.text_input("Securities (comma separated)")
    bm = st.text_input("Benchmark")
    rfr = st.text_input("Risk-free rate")

    securities = []
    if text:
        securities = [x.strip() for x in text.split(",") if x.strip()]

    market = st.segmented_control('Market', ['All', 'Up', 'Down'], default='All')
    ci = st.slider('Confidence interval', min_value=0.9, max_value=0.995, value=0.95, step=0.005, format='percent')
    bin_size = st.slider('Bin size', min_value=0.005, max_value=0.1, value=0.01, step=0.005, format='percent')

raw = get_data()
mask = pd.Series(True, index=raw.index)
match market:
    case 'Up':
        mask = raw['Fund'] >= 0
    case 'Down':
        mask = raw['Fund'] < 0
data = raw[mask]

# Series
fund = data['Fund']
benchmark = data['Benchmark']
rfr = data['Rfr']

# Long format without Rfr
df = data.melt(var_name='Series', value_name='Return')
df = df.loc[df['Series'] != 'Rfr']

perf = pd.Series({
    'Annualized Return': ftk.compound_return(fund, annualize=True),
    'Cumulative Return': ftk.compound_return(fund, annualize=False),
    'Average Return': ftk.arithmetic_mean(fund),
    'Average Positive Return': ftk.avg_pos(fund),
    'Average Negative Return': ftk.avg_neg(fund),
    'Observations': fund.count(),
    'Best Period': ftk.best_period(fund),
    'Worst Period': ftk.worst_period(fund),
    'Annualized Excess Return': ftk.active_return(fund, benchmark, annualize=True),
    'Cumulative Excess Return': ftk.active_return(fund, benchmark, annualize=False),
}).to_frame(name='').style.format("{:.2%}")
perf.index.name = 'Performance'

risk = pd.Series({
    'Annualized Volatility': ftk.volatility(fund, annualize=True),
    'Annualized Variance': ftk.variance(fund, annualize=True),
    'Skewness': ftk.skew(fund),
    'Excess Kurtosis': ftk.kurt(fund),
    'Max Drawdown': ftk.worst_drawdown(fund),
    'Average Drawdown': ftk.all_drawdown(fund).mean(),
}).to_frame(name='').style.format("{:.2%}")
risk.index.name = 'Risk'

var = pd.Series({
    'Gaussian VaR': ftk.var_normal(fund, sig=1-ci),
    'Cornish-Fisher VaR': ftk.var_modified(fund, sig=1-ci),
    'Gaussian CVaR': ftk.cvar_normal(fund, sig=1-ci)
}).to_frame(name='').style.format("{:.2%}")
var.index.name = 'Value at Risk'

regression = pd.Series({
    'Beta': ftk.beta(fund, benchmark),
    'Beta (Rfr Adjusted)': ftk.beta(fund - rfr, benchmark - rfr),
    'Correlation': ftk.correlation(pd.concat([fund, benchmark], axis=1)).iloc[0, -1],
    'R²': ftk.rsquared(fund, benchmark),
    #'Annualized Alpha': ftk.alpha(fund, benchmark, annualize=True),
    #'Jensen''s Alpha': ftk.alpha(fund - rfr, benchmark - rfr, annualize=True),
    'Autocorrelation': ftk.correlation(pd.concat([fund.iloc[1:], fund.iloc[1:].shift(-1)], axis=1)).iloc[0, -1],
}).to_frame(name='').style.format("{:.2%}")
regression.index.name = 'Regression'

efficiency = pd.Series({
    'Tracking Error': ftk.tracking_error(fund, benchmark, annualize=True),
    'Information Ratio': ftk.information_ratio(fund, benchmark),
    'Up Capture': ftk.up_capture(fund, benchmark),
    'Down Capture': ftk.down_capture(fund, benchmark),
    'Sortino': ftk.sortino(fund),
    'Calmar': ftk.calmar(fund),
}).to_frame(name='').style.format("{:.2%}")
efficiency.index.name = 'Efficiency'


st.title('Performance and Risk Analysis')

vami = ftk.return_to_price(pd.concat([fund, benchmark], axis=1))
vami.index.name = 'Date'
vami = vami.reset_index().melt(id_vars='Date', var_name='Series', value_name='Return')
vami['Return'] = vami['Return'] - 1
line = alt.Chart(vami).mark_line().encode(
    x='Date',
    y=alt.Y('Return', title='Cumulative Return', axis=alt.Axis(format='%')),
    color=alt.Color('Series', scale=alt.Scale(domain=['Fund', 'Benchmark']), legend=alt.Legend(orient='top', title=None))
)
line

histogram = alt.Chart(df).mark_bar().encode(
    alt.X('Return', bin=alt.Bin(step=bin_size), axis=alt.Axis(format='%')),
    alt.Y('count()', title='Count', stack=None),
    color=alt.Color('Series', scale=alt.Scale(domain=['Fund', 'Benchmark']))
).facet(column=alt.Column('Series', sort=['Fund', 'Benchmark'], header=alt.Header(
            title=None
        )))
histogram

col1, col2, col3 = st.columns(3)

col1.dataframe(perf)

with col2:
    st.dataframe(risk)
    st.dataframe(var)

with col3:
    st.dataframe(regression)
    st.dataframe(efficiency)