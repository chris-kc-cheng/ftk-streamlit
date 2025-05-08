# Streamlit web apps using Financial Toolkit

[Streamlit](https://streamlit.io/) is a powerful framework that transforms Python scripts into interactive web applications.

In this repository, I have created several web apps that demonstrate common use cases in investment management, leveraging the [Financial Toolkit](https://github.com/chris-kc-cheng/financial-toolkit).

## App 1: Market Index Data

This web app retrieves data on major equity indices and currencies from Yahoo! Finance and displays their performance using interactive charts and tables. The currency and time horizon are fully customizable.

<a href="https://ftk-indices.streamlit.app/">
    <img alt='Indices' src='images/indices.png' style='border: none' />
    👆 Click the image above to launch the web app.
</a>

## App 2: Fama-French Factor Analysis

This web app retrieves the returns of a user-specified fund and analyzes its factor loadings using the Fama-French model.

<a href="https://ftk-factors.streamlit.app/">
    <img alt='Factor Analysis' src='images/factors.png' style='border: none' />
    👆 Click the image above to launch the web app.
</a>

## App 3: Portfolio Optimization

This web app compares the risk–reward profiles and risk contributions of various portfolio weighting schemes, such as Risk Parity, Maximum Sharpe Ratio, and Minimum Volatility. The asset mix, constraints, and time horizon are all fully customizable.

<a href="https://ftk-portfolio-optimization.streamlit.app/">
    <img alt='Portfolio Optimiazation' src='images/portfolio.png' style='border: none' />
    👆 Click the image above to launch the web app.
</a>

## App 4: Peer Group Analysis

This web app compares the performance and risk metrics of a peer group against a benchmark. Users can define their investment universe and benchmark via URL parameters using the following format:

`https://ftk-peers.streamlit.app/?fund=FUND1&fund=FUND2&benchmark=BM`

<a href="https://ftk-peers.streamlit.app/?fund=PRCOX&fund=GQEFX&fund=STSEX&fund=NUESX&fund=VTCLX&fund=CAPEX&fund=USBOX&fund=VPMCX&fund=JDEAX&fund=DFUSX&fund=GALLX&benchmark=%5ESP500TR">
    <img alt='Peer Group Analysis' src='images/peers.png' style='border: none' />
    👆 Click the image above to launch the web app.
</a>

## App 5: Option Strategies

This web app presents the values of individual securities and the total payoffs of various option strategies. Theoretical option values are calculated using the Black-Scholes model. Additional charts illustrate how the Greeks change across different spot prices.

<a href="https://ftk-options.streamlit.app/">
    <img alt='Option Strategies' src='images/options.png' style='border: none' />
    👆 Click the image above to launch the web app.
</a>


The source code is hosted on GitHub at: https://github.com/chris-kc-cheng/ftk-streamlit.