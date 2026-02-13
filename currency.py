import pandas as pd
import streamlit as st
import altair as alt
import toolkit as ftk


@st.cache_data(ttl=3600)
def get_data():
    data = pd.read_csv('data/indices.csv', index_col=0)
    data = data[data['Group'] == 'Currency'].drop(
        columns=['Currency', 'Group'])
    fx = ftk.get_yahoo_bulk(data.index, '2y')
    return fx, data


def get_flag(code):
    return f'https://flagpedia.net/data/{"org" if code == "EU" else "flags"}/w320/{code.lower()}.png'


fx, data = get_data()
fx = fx.drop(columns=['USD=X']).dropna()
fx.index = fx.index.date

with st.sidebar:

    st.logo('images/icon.png', icon_image='images/icon.png', size='large')
    from_date, to_date = st.select_slider(
        'Period', options=fx.index, value=(fx.index[-252], fx.index[-1]))
    show = st.segmented_control('Show', ['Quote', 'Change'], default='Quote')

filtered = fx.T[[from_date, to_date]]
merged = filtered.join(data)
merged = pd.concat([merged, pd.DataFrame({
    from_date: 1.,
    to_date: 1.,
    'Name': 'US Dollar',
    'Country': 'US'
}, index=['USD=X'])]).reset_index()
merged['index'] = merged['index'].str[:-2]

matrix = pd.merge(merged, merged.add_prefix('FC'), how='cross')
matrix = matrix.rename(columns={
    'index': 'DC_ISO',
    from_date: 'DC_0',
    to_date: 'DC_1',
    'Name': 'DC_Name',
    'Country': 'DC_Country',
    'FCindex': 'FC_ISO',
    'FC'+str(from_date): 'FC_0',
    'FC'+str(to_date): 'FC_1',
    'FCName': 'FC_Name',
    'FCCountry': 'FC_Country'
})

matrix['Quote'] = matrix['DC_ISO'] + '/' + matrix['FC_ISO']
matrix['FX_1'] = matrix['FC_1'] / matrix['DC_1']
matrix['FX_0'] = matrix['FC_0'] / matrix['DC_0']
matrix['FX_C'] = matrix['FX_1'] / matrix['FX_0'] - 1
matrix['DC_Country'] = matrix['DC_Country'].apply(get_flag)
matrix['FC_Country'] = matrix['FC_Country'].apply(get_flag)

tooltip = [
    alt.Tooltip('Quote:N', title='Quote'),
    alt.Tooltip('FX_C:Q', title='Change', format='.2%'),
    alt.Tooltip('FX_1:Q', title=str(to_date), format='.5g'),
    alt.Tooltip('FX_0:Q', title=str(from_date), format='.5g'),
]

# Heatmap
rng = max(abs(matrix['FX_C'].max()), abs(matrix['FX_C'].min()))

hover = alt.selection_point(
    fields=['FC_ISO', 'DC_ISO'],
    on='mouseover',
    empty='none'
)
brush = alt.selection_interval(encodings=["x"])

base = alt.Chart(matrix)
heatmap = base.mark_rect().encode(
    x=alt.X('FC_ISO:N', axis=None),
    y=alt.Y('DC_ISO:N', axis=None),
    color=alt.Color('FX_C:Q', scale=alt.Scale(
        domain=[-rng, 0, rng],
        range=['red', '#fefefe', 'green']
    ),
        legend=alt.Legend(format='.0%'),
        title='Change'
    ),
    tooltip=tooltip
).add_params(hover).properties(
    height=600,
    width=1200
)

# X-axis / Foreign Currency
x_images = base.mark_image(height=40).encode(
    x=alt.X('FC_ISO:N'),
    y=alt.value(-22),
    url='FC_Country'
)

# Y-axis / Domestic Currency
y_images = base.mark_image(width=60).encode(
    x=alt.value(-32),
    y=alt.Y('DC_ISO:N'),
    url='DC_Country'
)

text = base.mark_text().encode(
    x=alt.X('FC_ISO:N'),
    y=alt.Y('DC_ISO:N'),
    text=alt.Text('FX_1:Q', format='.5g') if show == 'Quote' else alt.Text(
        'FX_C:Q', format='.2%'),
    tooltip=tooltip
)

chart = heatmap + x_images + y_images + text

# Filtered time series
ts = fx
ts.index.name = 'Date'
ts = ts.reset_index().melt(id_vars='Date', var_name='DC_ISO', value_name='Rate')
ts['DC_ISO'] = ts['DC_ISO'].str[:-2]
ts = pd.merge(ts, ts.add_prefix('FC'), left_on='Date', right_on='FCDate')
ts['Rate'] = ts['FCRate'] / ts['Rate']
ts = ts.rename(columns={'FCDC_ISO': 'FC_ISO'}).drop(
    columns=['FCDate', 'FCRate'])
x = ts.merge(matrix, left_on=['DC_ISO', 'FC_ISO'],
             right_on=['DC_ISO', 'FC_ISO'], how='inner')

line = alt.Chart(x).mark_line().encode(
    x='Date:T',
    y='Rate:Q'
).transform_filter(hover)

# Page
col1, col2 = st.columns(2)
col1.title('Foreign Exchange')

st.altair_chart(chart, width='content')  # chart & line, too slow

with st.expander('Data', expanded=False):
    st.dataframe(matrix.drop(
        columns=['DC_Name', 'DC_Country', 'FC_Name', 'FC_Country']))
