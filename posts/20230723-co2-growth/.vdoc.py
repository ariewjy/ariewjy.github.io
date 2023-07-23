# type: ignore
# flake8: noqa
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#importing dataset

import pandas as pd
import warnings

# Ignore future warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'

co2_raw = pd.read_csv('https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv')
co2_remark = pd.read_csv('https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-codebook.csv')
co2_raw
#
#
#
#
#
#selecting dataset
co2 = co2_raw[[ 'country', 'year','population', 'gdp', 'co2_per_capita', 'consumption_co2_per_capita' ]]

#adding gdp per capita column
co2['gdp_per_capita'] = co2['gdp']/ co2['population']

# dropping any rows with null consumption_co2_per_capita
co2 = co2[~co2.consumption_co2_per_capita.isnull()].reset_index(drop=True)

#drop gdp column
co2 = co2.drop(columns='gdp')

#removing any incomplete data
co2 = co2.query(" gdp_per_capita>0 & co2_per_capita>0")
co2.dropna().sample(5)
#
#
#
#
#
#
#
#importing gapminder
gapminder=pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')
gapminder = gapminder[['country', 'continent']]
gapminder = gapminder.drop_duplicates().reset_index(drop=True)

#merging with original co2 dataset
co2 = pd.merge(co2, gapminder, on='country', how='inner')

#drop consumption per capita
co2 = co2.drop(columns='consumption_co2_per_capita')

#sanity check
co2
#
#
#
#
#
#
#
#creating income class category based on gdp per capita. 

bins= [0.00001,1000,4000,12000,1000000] #setting up the group based on bmi bins 
labels = [
         'lower',
         'lower-middle',
         'upper-middle',
         'upper'
         ] #setting up the label on each group

co2['income_class']= pd.cut(
   co2['gdp_per_capita'], 
   bins=bins, 
   labels=labels,
   include_lowest=False
   )

co2
#
#
#
#
#
#
#
#
#
#
#

#| label: fig-timeplot
#| fig-cap: 1990-2018 Time-lapse Chart of CO2 Emission and GDP per Country

import plotly_express as px

source = co2

#selected countries to annotate
highlighted_countries = ['United States', 'Germany', 'United Kingdom',
                         'China', 'Singapore','Mexico', 'India', 'Indonesia', 
                         'Nigeria', 'Vietnam', 'Bangladesh', 'Ethiopia'
                        ]

# Create a new column for text values based on the condition
source['text_value'] = source['country'].apply(lambda country: country if country in highlighted_countries else '')

fig = px.scatter(data_frame=source, 
           x="co2_per_capita", 
           y="gdp_per_capita", 
           animation_frame="year", 
           animation_group="country",
           size="population", 
           color="continent", 
           hover_name="country", 
           log_x = True, log_y=True,
           size_max=70,
           width=800,
           height=800,
           # text_baseline='bottom',
           range_x=[0.01,100], 
           range_y=[400,90000],
           text='text_value'
          )


fig.update_layout(
    # title='CO2 Emission vs GDP of Countries',
    xaxis_title='CO2 Emission per Capita (tonnes)',
    yaxis_title='GDP per Capita (USD)',
    legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
)
)

fig.show()
#
#
#
#
#
#
#
#
#

#| label: fig-co2-gdp-cluster
#| fig-cap: CO2 vs GDP per Capita for some countries with different trend

import altair as alt

highlighted_countries = ['India', 'Indonesia', 'United Kingdom', 'Germany', 'United States']

source=co2[co2['country'].isin(highlighted_countries)]

alt.Chart(
    source,
    title=alt.Title(
        "GDP per Capita vs CO2 Emission",
        subtitle=["Different CO2 vs GDP rate in different Countries"]
    )
    ).mark_point(size=90, filled=True, opacity=0.7).encode(
    x=alt.X(
        'co2_per_capita:Q', title='CO2 per Capita',
        scale=alt.Scale(type="log", domain=[0.3, 30])
        ),
    y=alt.Y(
        'gdp_per_capita:Q', title='GDP per Capita',
        scale=alt.Scale(type="log")
        ),
    color=alt.Color('year', title='Year'),
    shape='country',
    tooltip=['country', 'population', 'co2_per_capita', 'gdp_per_capita']
).properties(
    width=500,
    height=500,
).interactive()
#
#
#
#
# create a column for gdp changes between 1990-2018

# Pivot the DataFrame to have years as columns
gdp_df = co2.pivot(index='country', columns='year', values='gdp_per_capita')
# pivoted_df

# Calculate the difference between GDP values for years 1980 and 2018
gdp_df['gdp_diff'] = gdp_df[2018] - gdp_df[1990]

# Reset the index to convert the DataFrame back to the original format
gdp_df.reset_index(inplace=True)

# Merge the calculated difference back to the original DataFrame
merged_df = pd.merge(co2, gdp_df[['country', 'gdp_diff']], on='country', how='left')

merged_df
#
#
#
# create a column for co2 changes between 1990-2018

# Pivot the DataFrame to have years as columns
co2_df = co2.pivot(index='country', columns='year', values='co2_per_capita')
# pivoted_df

# Calculate the difference between GDP values for years 1980 and 2018
co2_df['co2_diff'] = co2_df[2018] - co2_df[1990]

# Reset the index to convert the DataFrame back to the original format
co2_df.reset_index(inplace=True)

# Merge the calculated difference back to the original DataFrame
merged_df = pd.merge(merged_df, co2_df[['country', 'co2_diff']], on='country', how='left')
merged_df
#
#
#
merged_df['gdp_per_co2_rate'] = merged_df['gdp_diff']/merged_df['co2_diff']
merged_df
#
#
#
#negara dengan gdp yg NAIK dan EMISI turun --- very good country
merged_df.query(" gdp_diff>0 & co2_diff<0")
#
#
#

import hvplot.pandas 
import panel as pn

source=merged_df.query(" gdp_diff>0 & co2_diff<0")

source.hvplot.scatter(
    x='co2_per_capita', 
    y='gdp_per_capita',
    by='country',
    logx=True,
    xlim=[0.01,100], 
    ylim=[400,90000],
    logy=True,
    legend='top',
    height=600,
    width=800,
    hover_cols=['year']
)
#
#
#
source =merged_df.query(" gdp_diff>0 & co2_diff<0")

year_widget=pn.widgets.IntSlider(name='year', start=source.year.min(), end=source.year.max())

idf = source.interactive()
idf = idf[(idf['year'] == year_widget)]

idf.hvplot.scatter(
    x='co2_per_capita', 
    y='gdp_per_capita',
    by='income_class',
    s='size',
    logx=True,
    logy=True,
    xlim=[0.01,100], 
    ylim=[400,90000],
    legend='top',
    height=600,
    width=800,
    hover_cols=["country", "population"],
)
#
#
#
#negara dengan gdp yg TURUN dan EMISI turun
merged_df.query(" gdp_diff<0 & co2_diff<0")
#
#
#
source =merged_df.query(" gdp_diff<0 & co2_diff<0")
year_widget=pn.widgets.IntSlider(name='year', start=source.year.min(), end=source.year.max())

idf = source.interactive()
idf = idf[(idf['year'] == year_widget)]

idf.hvplot.scatter(
    x='co2_per_capita', 
    y='gdp_per_capita',
    by='country',
    s='size',
    logx=True,
    logy=True,
    xlim=[0.01,100], 
    ylim=[400,90000],
    legend='top',
    height=600,
    width=800,
    hover_cols=["country", "population"],
)
#
#
#
#negara dengan gdp yg NAIK dan EMISI naik
merged_df.query(" gdp_diff>0 & co2_diff>0")
#
#
#
source =merged_df.query(" gdp_diff>0 & co2_diff>0")

year_widget=pn.widgets.IntSlider(name='year', start=source.year.min(), end=source.year.max())

idf = source.interactive()
idf = idf[(idf['year'] == year_widget)]

idf.hvplot.scatter(
    x='co2_per_capita', 
    y='gdp_per_capita',
    by='continent',
    s='size',
    logx=True,
    logy=True,
    xlim=[0.01,100], 
    ylim=[400,90000],
    legend='top',
    height=600,
    width=800,
    hover_cols=["country", "population"],
)
#
#
#
