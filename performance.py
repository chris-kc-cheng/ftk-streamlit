import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import toolkit as ftk
import utils


@st.cache_data(ttl=3600)
def get_data(tickers) -> pd.DataFrame:
    data = ftk.get_yahoo_bulk(tickers).reindex(
        columns=[t.upper() for t in tickers])
    data = data.resample('ME').last()
    data.iloc[:, :2] = data.iloc[:, :2].pct_change()
    data.iloc[:, 2] = data.iloc[:, 2] / 12 / 100
    data.index = data.index.to_period('M')
    return data.dropna()


horizons = {
    '1Y': 12,
    '3Y': 36,
    '5Y': 60,
    '10Y': 120,
    'All': 0
}

sample = ['FCNTX', '^GSPC', '^IRX']
universe = None

if 'price' not in st.session_state:
    st.session_state.price = get_data(sample)

with st.sidebar:

    with st.expander('Public Security', expanded=True):
        with st.form('public_form', border=False):
            f = st.text_input('Fund / Stock', value=sample[0])
            b = st.text_input('Benchmark', value=sample[1])
            r = st.text_input('Risk-free rate', value=sample[2])
            submitted = st.form_submit_button('Search')
            if submitted:
                st.session_state.price = get_data([f, b, r])

    with st.expander('Proprietary Data', expanded=True):
        uploaded_file = st.file_uploader('Data File', type=['csv', 'xlsx'])
        if uploaded_file is not None:

            if uploaded_file.name.split('.')[-1] == 'csv':
                df = pd.read_csv(uploaded_file, header=0, index_col=0)
            else:
                df = pd.read_excel(uploaded_file, header=0, index_col=0)

            df.index = pd.to_datetime(df.index).to_period('M')
            df.index.name = 'Date'
            periods, securities = df.shape
            st.toast(
                f'Loaded {securities} securities and {periods} periods', icon='✅')
            universe = df

            securities = sorted(universe.columns)
            f = st.selectbox('Fund', securities,
                             index=securities.index(universe.columns[0]))
            b = st.selectbox('Benchmark', securities,
                             index=securities.index(universe.columns[1]))
            r = st.selectbox('Risk-free rate', securities,
                             index=securities.index(universe.columns[2]))
            with st.form('private_form', border=False):
                submitted = st.form_submit_button('Run')
                if submitted:
                    st.session_state.price = universe[[f, b, r]]

    with st.expander('Line Chart', expanded=True):
        annualize = st.toggle('Annualize', value=False)
        window = st.segmented_control(
            'Window', ['Cumulative', 'Trailing', 'Rolling'], default='Cumulative')
        if window == 'Rolling':
            size = st.slider('Window Size (Months)', 6, 120, value=36, step=6)
        grouping = st.segmented_control(
            'Group by', ['Measure', 'Security'], default='Measure')

    with st.expander('Page Setting', expanded=True):
        show = st.segmented_control(
            'Show', st.session_state.price.columns, default=st.session_state.price.columns[:2], selection_mode='multi')
        horizon = st.segmented_control(
            'Time Horizon', ['1Y', '3Y', '5Y', '10Y', 'All', 'Custom'], default='10Y')
        if horizon == 'Custom':
            date_range = st.select_slider(
                'Date Range',
                options=st.session_state.price.index,
                value=(st.session_state.price.index[0],
                       st.session_state.price.index[-1]),
                format_func=lambda d: d.strftime('%Y-%m-%d'))
        market = st.segmented_control(
            'Market', ['All', 'Up', 'Down'], default='All')
        ci = st.slider('Confidence interval', min_value=0.9,
                       max_value=0.995, value=0.95, step=0.005, format='percent')
        bin_size = st.slider('Bin size', min_value=0.005,
                             max_value=0.1, value=0.01, step=0.005, format='percent')
        decimals = st.segmented_control('Decimal Place', range(5), default=2)

raw = st.session_state.price
if len(raw) == 0:
    st.info('Search a fund, benchmark and risk free rate to continue')
    st.stop()

market_mask = pd.Series(True, index=raw.index)
match market:
    case 'Up':
        market_mask = raw.iloc[:, 0] >= 0
    case 'Down':
        market_mask = raw.iloc[:, 0] < 0
horizon_mask = -horizons[horizon] if horizon in horizons else None
data = raw[market_mask].iloc[horizon_mask:]
if horizon == 'Custom':
    data = data.loc[date_range[0]:date_range[1]]

# Series
fund = data.iloc[:, 0]
benchmark = data.iloc[:, 1]
rfr = data.iloc[:, 2]

data = data[show]

perf = pd.Series({
    'Annualized Return': ftk.compound_return(fund, annualize=True),
    'Cumulative Return': ftk.compound_return(fund, annualize=False),
    'Growth of $100': 100 * (1 + ftk.compound_return(fund, annualize=False)),
    'Observations': fund.count(),
    'Number of Positive Periods': fund[fund >= 0].count(),
    'Number of Negative Periods': fund[fund < 0].count(),
    'Average Return': ftk.arithmetic_mean(fund),
    'Average Positive Return': ftk.avg_pos(fund),
    'Average Negative Return': ftk.avg_neg(fund),
    'Best Period': ftk.best_period(fund),
    'Worst Period': ftk.worst_period(fund),
    'Max Consecutive Gain Return': ftk.max_consecutive_gain(fund),
    'Max Consecutive Loss Return': ftk.max_consecutive_loss(fund),
    'Number of Consecutive Positive Periods': ftk.consecutive_positive_periods(fund),
    'Number of Consecutive Negative Periods': ftk.consecutive_negative_periods(fund),
    'Cumulative Excess Return': ftk.active_return(fund, benchmark, annualize=False),
    'Annualized Excess Return': ftk.active_return(fund, benchmark, annualize=True),
    'Excess Returns - Geometric': ftk.excess_return_geometric(fund, benchmark),
    'Periods Above Benchmark': (fund - benchmark > 0).sum(),
    'Percentage Above Benchmark': (fund - benchmark > 0).mean(),
    'Percent Profitable Periods': (fund > 0).mean()
}).to_frame(name='').style.format(f'{{:.{decimals}%}}').format('${:.2f}', subset=pd.IndexSlice[['Growth of $100'], :]).format('{:,.0f}', subset=pd.IndexSlice[['Observations', 'Number of Positive Periods', 'Number of Negative Periods', 'Number of Consecutive Positive Periods', 'Number of Consecutive Negative Periods', 'Periods Above Benchmark'], :])
perf.index.name = 'Performance'

risk = pd.Series({
    'Annualized Volatility': ftk.volatility(fund, annualize=True),
    'Annualized Variance': ftk.variance(fund, annualize=True),
    'Skewness': ftk.skew(fund),
    'Excess Kurtosis': ftk.kurt(fund),
    'Jarque-Bera': ftk.jarque_bera(fund),
    'Max Drawdown': ftk.worst_drawdown(fund),
    'Average Drawdown': ftk.all_drawdown(fund).mean(),
    'Current Drawdown': ftk.current_drawdown(fund),
    'Semi Deviation': ftk.semi_deviation(fund),
    'Gain Deviation (MAR)': ftk.downside_risk(-fund, 0, annualize=True),
    'Loss Deviation': ftk.downside_risk(fund, rfr, ddof=0, annualize=True),
    'Bias Ratio': ftk.bias_ratio(fund),
    'Gain/Loss Ratio': ftk.gain_loss(fund),
}).to_frame(name='').style.format(f'{{:.{decimals}%}}').format(f'{{:.{decimals}f}}', subset=pd.IndexSlice[['Skewness', 'Excess Kurtosis', 'Jarque-Bera', 'Bias Ratio', 'Gain/Loss Ratio'], :])
risk.index.name = 'Risk'

var = pd.Series({
    'Gaussian VaR': ftk.var_normal(fund, sig=1-ci),
    'Cornish-Fisher VaR': ftk.var_modified(fund, sig=1-ci),
    'Gaussian CVaR': ftk.cvar_normal(fund, sig=1-ci)
}).to_frame(name='').style.format(f'{{:.{decimals}%}}')
var.index.name = 'Value at Risk'

regression = pd.Series({
    'Beta': ftk.beta(fund, benchmark),
    'Beta T-Stat': ftk.beta_t_stat(fund, benchmark),
    'Beta (Rfr Adjusted)': ftk.beta(fund - rfr, benchmark - rfr),
    'Alpha (Annualized)': ftk.alpha(fund, benchmark, annualize=True, legacy=True),
    'Jensen Alpha': ftk.alpha(fund, benchmark, rfr, annualize=True, legacy=True),
    'Correlation': ftk.correlation(pd.concat([fund, benchmark], axis=1)).iloc[0, -1],
    'R²': ftk.rsquared(fund, benchmark),
    'Standard Error of Regression': ftk.ser(fund, benchmark),
    'Autocorrelation': ftk.correlation(pd.concat([fund.iloc[1:], fund.iloc[1:].shift(-1)], axis=1)).iloc[0, -1],
}).to_frame(name='').style.format(f'{{:.{decimals}%}}').format(f'{{:.{decimals}f}}', subset=pd.IndexSlice[['Beta', 'Beta T-Stat', 'Beta (Rfr Adjusted)', 'Correlation', 'Standard Error of Regression', 'Autocorrelation'], :])
regression.index.name = 'Regression'

efficiency = pd.Series({
    'Sharpe Ratio': ftk.sharpe(fund, rfr),
    'Reward to Risk Ratio': ftk.reward_to_risk(fund),
    'Treynor Ratio': ftk.treynor(fund, benchmark, rfr),
    'Sortino Ratio': ftk.sortino(fund, rfr),
    'Sterling Ratio': ftk.sterling_modified(fund),
    'Calmar Ratio': ftk.calmar(fund),
    'Up Market Return': ftk.up_market_return(fund, benchmark),
    'Down Market Return': ftk.down_market_return(fund, benchmark),
    'Up Capture': ftk.up_capture(fund, benchmark),
    'Down Capture': ftk.down_capture(fund, benchmark),
    'Tracking Error': ftk.tracking_error(fund, benchmark, annualize=True),
    'Information Ratio': ftk.information_ratio(fund, benchmark),
    'Batting Average': ftk.batting_average(fund, benchmark),
    'Up Period Batting Average': ftk.up_batting_average(fund, benchmark),
    'Down Market Batting Average': ftk.down_batting_average(fund, benchmark),
    'Rolling Batting Average': ftk.rolling_batting_average(fund, benchmark),
}).to_frame(name='').style.format(f'{{:.{decimals}%}}').format(f'{{:.{decimals}f}}', subset=pd.IndexSlice[['Sharpe Ratio', 'Reward to Risk Ratio', 'Treynor Ratio', 'Sortino Ratio', 'Sterling Ratio', 'Calmar Ratio', 'Information Ratio'], :])
efficiency.index.name = 'Efficiency'


st.title('Performance and Risk Analysis')

measure_options = {
    'Return': lambda x: ftk.compound_return(x, annualize),
    'Volatility': lambda x: ftk.volatility(x, annualize),
    'VaR': lambda x: ftk.var_normal(x, 1-ci),
    'CVaR': lambda x: ftk.cvar_normal(x, 1-ci),
    'Autocorrelation': ftk.autocorrelation,
    'Drawdown': ftk.current_drawdown,
    'Risk Reward': ftk.reward_to_risk,
    'Sharpe': lambda x: ftk.sharpe(x, rfr.reindex(x.index), annualize=annualize),
    'Tracking Error': lambda x: ftk.tracking_error(x, benchmark.reindex(x.index), annualize=annualize),
    'Beta': lambda x: ftk.beta(x, benchmark.reindex(x.index)),
}
measure_selected = st.multiselect('Measure', sorted(measure_options.keys()),
                                  default=['Return', 'Volatility'])
measures = {k: v
            for k, v in measure_options.items() if k in measure_selected}

match window:
    case "Rolling":
        line_data = data.rolling(size)
    case "Trailing":
        line_data = data[::-1].expanding(min_periods=12)
    case _:  # Cumulative
        line_data = data.expanding(min_periods=12)

try:
    line_data = pd.concat({
        label: line_data.apply(func)
        for label, func in measures.items()
    })
    line_data.index.names = ['Measure', 'Date']
    line_data = line_data.reset_index().melt(
        id_vars=['Measure', 'Date'], var_name='Series', value_name='Value')
    line_data['Date'] = line_data['Date'].dt.to_timestamp()
    line = alt.Chart(line_data).mark_line().encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m')),
        y=alt.Y('Value', title='Measure', axis=alt.Axis(format='%')),
        color=alt.Color('Measure', legend=alt.Legend(orient='top', title=None))
        if grouping == 'Security' else
        alt.Color('Series', scale=alt.Scale(domain=raw.columns),
                  legend=alt.Legend(orient='top', title=None))
    ).facet(column=alt.Column('Series' if grouping == 'Security' else 'Measure', header=alt.Header(
        title=None
    )))
    st.altair_chart(line)
except:
    st.warning('Select at least one measure')

# Long format without Rfr
histogram_data = data
histogram_data = histogram_data.melt(var_name='Series', value_name='Return')

histogram = alt.Chart(histogram_data).mark_bar().encode(
    alt.X('Return', bin=alt.Bin(step=bin_size), axis=alt.Axis(format='%')),
    alt.Y('count()', title='Count', stack=None),
    color=alt.Color('Series', scale=alt.Scale(domain=raw.columns))
).facet(
    column=alt.Column('Series', sort=raw.columns, header=alt.Header(
        title=None)),
    columns=3
)

st.altair_chart(histogram)

# Tables
col1, col2, col3 = st.columns(3)

with col1:
    st.table(perf)

with col2:
    st.table(risk)
    st.table(var)

with col3:
    st.table(regression)
    st.table(efficiency)

with st.expander('Table', expanded=True):
    for i, tab in enumerate(st.tabs(list(raw.columns))):
        tab.dataframe(utils.format_table(raw.iloc[:, i]))
