import math
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt


def cir(years: float, a: float, b: float, sigma: float, init: float, scenarios: int = 1, steps_per_year: int = 12) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Cox-Ingersoll-Ross model for interest rate simulation

    Parameters
    ----------
    years : float
        Number of years
    a : float
        Speed of mean reversion
    b : float
        Long-term average rate
    sigma : float
        Annualized volatility
    init : float
        Initial rate
    scenarios : int, optional
        Number of simulations, by default 1
    steps_per_year : int, optional
        Steps per year, by default 12

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        Rates, and zero-coupon bond prices
    """

    init = np.log1p(init)
    dt = 1/steps_per_year
    n = int(years * steps_per_year) + 1

    shock = np.random.normal(0, scale=np.sqrt(dt), size=(n, scenarios))
    rates = np.empty_like(shock)
    rates[0] = init

    h = math.sqrt(a**2 + 2*sigma**2)
    prices = np.empty_like(shock)

    def price(ttm, r):
        _A = ((2*h*math.exp((h+a)*ttm/2)) /
              (2*h+(h+a)*(math.exp(h*ttm)-1)))**(2*a*b/sigma**2)
        _B = (2*(math.exp(h*ttm)-1))/(2*h + (h+a)*(math.exp(h*ttm)-1))
        _P = _A*np.exp(-_B*r)
        return _P

    prices[0] = price(years, init)

    for step in range(1, n):
        r_t = rates[step-1]
        d_r_t = a*(b-r_t)*dt + sigma*np.sqrt(r_t)*shock[step]
        rates[step] = abs(r_t + d_r_t)
        prices[step] = price(years-step*dt, rates[step])

    rates = pd.DataFrame(data=np.expm1(rates), index=range(n))
    prices = pd.DataFrame(data=prices, index=range(n))
    return rates, prices


with st.sidebar:

    scenarios = st.slider('Scenarios', min_value=1,
                          max_value=1000, value=100)
    years = st.slider('Years', min_value=0.25,
                      max_value=30., step=0.25, value=5.)
    steps_per_year = st.slider('Steps per year', min_value=1,
                               max_value=12, value=4)
    a = st.slider('Speed of mean reversion', min_value=0.,
                  max_value=10., value=0.5)
    b = st.slider('Long-term average rate', min_value=0.,
                  max_value=0.1, value=0.05, step=0.001, format='percent')
    sigma = st.slider('Volatility', min_value=0.,
                      max_value=0.1, value=0.01, step=0.001, format='percent')
    r0 = st.slider('Initial rate', min_value=0.,
                   max_value=0.1, value=0.02, step=0.001, format='percent')

st.title("Asset Liability Management")

rates, prices = cir(years=years, a=a, b=b, sigma=sigma, init=r0,
                    scenarios=scenarios, steps_per_year=steps_per_year)

st.header("Cox-Ingersoll-Ross Model")
st.line_chart(rates, x_label="Time", y_label="Rates",)
st.line_chart(prices, x_label="Time", y_label="Bond Prices",)

st.markdown(open('data/signature.md').read())
