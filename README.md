# Streamlit web apps using Financial Toolkit

[Streamlit](https://streamlit.io/) is a powerful framework that transforms Python scripts into interactive web applications.

In this repository, I have created several web apps that demonstrate common use cases in investment management, leveraging the [Financial Toolkit](https://github.com/chris-kc-cheng/financial-toolkit).

Click the badge below to launch the web app — a lightweight alternative to Bloomberg.

<a href="https://terminal.streamlit.app/">
    <img src='https://static.streamlit.io/badges/streamlit_badge_black_white.svg' alt='Play' style='border: none;' />
</a>

## App 10: Foreign Exchange

This web application visualizes cross-currency exchange rates in a heatmap format, displaying real-time quotes and corresponding percentage changes.

<a href="https://terminal.streamlit.app/currency">
    <img alt='Yield Curve' src='images/currency.png' style='border: none' />
</a>

## App 9: Periodic Table

This web app displays a periodic-table-style summary of returns across different asset classes and hedge fund strategies. Users can customize the table by selecting different time horizons, adjusting conditional formatting, changing the order, and choosing the reference point.

<a href="https://terminal.streamlit.app/heatmap">
    <img alt='Yield Curve' src='images/heatmap.gif' style='border: none' />
</a>

## App 8: Yield Curve

This web app shows how the Canadian and US yield curves move over time.

<a href="https://terminal.streamlit.app/yield">
    <img alt='Yield Curve' src='images/yield.png' style='border: none' />
</a>

## App 7: Economic Indicators

This web app tracks Canadian and US economic indicators (CPI and unemployment rate) over time.

<a href="https://terminal.streamlit.app/economic">
    <img alt='Economic Indicators' src='images/economic.png' style='border: none' />
</a>

## App 6: Asset Liability Management

The web app uses the Cox–Ingersoll–Ross (CIR) model to generate interest-rate scenarios that evolve over time while reverting toward a long-term level.

<a href="https://terminal.streamlit.app/alm">
    <img alt='Asset Liability Management' src='images/alm.png' style='border: none' />
</a>

## App 5: Market Index Data

This web app retrieves data on major equity indices and currencies from Yahoo! Finance and displays their performance using interactive charts and tables. The currency and time horizon are fully customizable.

<a href="https://terminal.streamlit.app/">
    <img alt='Indices' src='images/indices.png' style='border: none' />
</a>

## App 4: Fama-French Factor Analysis

This web app retrieves the returns of a user-specified fund and analyzes its factor loadings using the Fama-French model.

<a href="https://terminal.streamlit.app/factors">
    <img alt='Factor Analysis' src='images/factors.png' style='border: none' />
</a>

## App 3: Portfolio Optimization

This web app compares the risk–reward profiles and risk contributions of various portfolio weighting schemes, such as Risk Parity, Maximum Sharpe Ratio, and Minimum Volatility. The asset mix, constraints, and time horizon are all fully customizable.

<a href="https://terminal.streamlit.app/portfolio">
    <img alt='Portfolio Optimiazation' src='images/portfolio.png' style='border: none' />
</a>

## App 2: Peer Group Analysis

This web app compares the performance and risk metrics of a peer group against a benchmark. Users can define their investment universe and benchmark via URL parameters using the following format:

`https://terminal.streamlit.app/peers?fund=FUND1&fund=FUND2&benchmark=BM`

<a href="https://terminal.streamlit.app/peers?fund=PRCOX&fund=GQEFX&fund=STSEX&fund=NUESX&fund=VTCLX&fund=CAPEX&fund=USBOX&fund=VPMCX&fund=JDEAX&fund=DFUSX&fund=GALLX&benchmark=%5ESP500TR">
    <img alt='Peer Group Analysis' src='images/peers.png' style='border: none' />
</a>

## App 1: Option Strategies

This web app presents the values of individual securities and the total payoffs of various option strategies. Theoretical option values are calculated using the Black-Scholes model. Additional charts illustrate how the Greeks change across different spot prices.

<a href="https://terminal.streamlit.app/options">
    <img alt='Option Strategies' src='images/options.png' style='border: none' />
</a>

The source code is hosted on GitHub at: https://github.com/chris-kc-cheng/ftk-streamlit.
