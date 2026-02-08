import streamlit as st
import pandas as pd

df = pd.DataFrame({
    "Label": ["Good", "Bad", "Neutral", "Good", "Bad"],
    "Score": [0.8, -0.4, 0.1, 0.9, -0.7]
})

def color_label(row):
    return ["background-color: lightgreen"] if row["Score"] > 0 else ["background-color: lightcoral"]

styled = (
    df.style
      .apply(color_label, axis=1, subset=["Label"])
      #.hide_columns(["Score"])
)

st.dataframe(styled)