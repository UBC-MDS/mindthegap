from dash import Dash, html, dcc, Input, Output
import numpy as np
import pandas as pd
import altair as alt
from vega_datasets import data
import dash_bootstrap_components as dbc



app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server=app.server

#dictionary to generate dynamic metrics in altair
metrics={'life_expectancy':'Life Expectancy', 'child_mortality':'Child Mortality', 'pop_density':'Population Density'}

#merge country_id.csv with gaominder.csv
gap = pd.read_csv('../data/gapminder.csv')
country_ids=pd.read_csv('../data/country_ids.csv')
gap = gap.merge(country_ids, how="outer", on=["country"])

# add log income for bubble chart
gap["log_income"] = gap["income"].apply(np.log)

@app.callback(
    Output("map", "srcDoc"),
    Input("metric", "value"),
    Input("yr", "value"),
)
def plot(metric, yr):
    return plot_world_map(metric, yr)

def filter_year(yr):
    return gap.loc[gap['year']==yr]

def plot_world_map(metric, yr):

    world = data.world_110m()
    world_map = alt.topo_feature(data.world_110m.url, 'countries')
    alt.data_transformers.disable_max_rows()
    df = filter_year(yr)

    chart = alt.Chart(world_map, title=f"{metrics[metric]} by country for year {yr}").mark_geoshape(stroke="black").transform_lookup(lookup="id", from_=alt.LookupData(df, key="id", fields=["country", metric])
            ).encode(
                tooltip=["country:O", metric + ":Q"],
                color=alt.Color(metric + ":Q", title=metrics[metric]))
    return chart.to_html()

boxPlot = html.Iframe(
    id="boxPlot",
    style={
        "border-width": "0",
        "width": "100%",
        "height": "400px"
    },
)

bubble_chart = html.Iframe(
    id="bubble_chart",
    style={
        "border-width": "0",
        "width": "100%",
        "height": "400px"
    },
)

barchart = html.Iframe(
    id='barchart',
    style={
        'border-width': '0', 
        'width': '100%',
        'height': '400px',
    },
)

app.layout = html.Div([
    
    dcc.RadioItems(id='metric', value='life_expectancy',
        options=[{'label': v, 'value': k} for k, v in metrics.items()]),
    html.Br(),
    'Year',
    dcc.Dropdown(id='yr', 
        options=[
                {'label': 1990, 'value': 1990},
                {'label': 2000, 'value': 2000},
                {'label': 2012, 'value': 2012},
                {'label': 2015, 'value': 2015}
                ],
            value=2012) ,
    html.Br(),
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Row(
                        html.Iframe(
                            id='map',
                            style={'border-width': '0', 'width': '100%', 'height': '600px'}
                        )
                    ),
                    dbc.Row(boxPlot),
                    dbc.Row(bubble_chart),
                    dbc.Row(barchart)
                ],
                md=8,
            ),
        ],
        align="center",
    ),
])

@app.callback(
    Output("boxPlot", "srcDoc"),
    Input("metric", "value"),
    # Input("region", "value"),
    # Input("sub_region", "value"),
    # Input("country", "value"),
    Input("yr", "value"),
)
# def plot_box_plot(metric, region, sub_region, country, yr):
def plot_box_plot(metric, yr):
    """
    Create box chart for statsitic of interested based on selected filters, for top 5 or bottom 5 countries
    Parameters
    --------
    metric: string
        Selection from statistic of interest filter
    region: string
        Selection from the region filter
    sub_region: sting
        Selection from Sub Region filter
    country: string
        Selection from Country filter
    year: integer
        Year for which the data is displayed, from Year filter
    Returns
    --------
    chart
        bar chart showing statistic of interest for top 5 or bottom 5 countries,
        in specific region, subregion, income group and year
    Example
    --------
    > plot_box_plot("child_mortality", "Asia", "Western Asia", "Yemen", 2015)
    """
    alt.data_transformers.disable_max_rows()

    # filter by region, sub-region, country & year
    data = filter_data(None, None, None, yr)
    # data = filter_data(region, sub_region, country, yr)
    
    data = data[data['income_group'].notnull()]

    chart = (
        alt.Chart(
            data,
            title=f"{metrics[metric]} group by Income Group for year {yr}",
        )
        .mark_boxplot()
        .encode(
            x=alt.X("income_group", sort="-x", title="Income Group"),
            y=alt.Y(metric, title=metrics[metric]),
            color=alt.Color(
                "income_group",
                sort=alt.EncodingSortField("income_group", order="descending"),
                title="Income Group",
            ),
            tooltip=("name:O", "child_mortality:Q"),
        )
        .configure_axis(labelFontSize=12, titleFontSize=14)
        .configure_title(fontSize=15)
        .configure_legend(labelFontSize=12)
        .properties(width=400, height=300)
    )
    return chart.to_html()

def filter_data(region, sub_region, country, yr):
    """
    Filter data based on region, sub region and income group selection
    Parameters
    --------
    region: string
        Selection from the Region filter
    sub_region: sting
        Selection from Sub Region filter
    country: sting
        Selection from Country filter
    yr: string
        Selection from  Year
    Returns
    --------
    data
        dataset that has been filtered on region, sub region and income group selection
    Example
    --------
    > filter_data(d"Asia", "Western Asia", "Yemen", 2015)
    """
    if region is not None and sub_region is not None and country is not None:
        data = gap[
            (gap["region"] == region)
            & (gap["sub_region"] == sub_region)
            & (gap["country"] == country)
        ]
    elif region is not None and sub_region is None and country is None:
        data = gap[(gap["region"] == region)]
    elif region is None and sub_region is not None and country is None:
        data = gap[(gap["sub_region"] == sub_region)]
    elif region is None and sub_region is None and country is not None:
        data = gap[(gap["country"] == country)]
    elif region is not None and sub_region is not None and country is None:
        data = gap[
            (gap["region"] == region) & (gap["sub_region"] == sub_region)
        ]
    elif region is None and sub_region is not None and country is not None:
        data = gap[
            (gap["sub_region"] == sub_region)
            & (gap["country"] == country)
        ]
    elif region is not None and sub_region is None and country is not None:
        data = gap[
            (gap["region"] == region) & (gap["country"] == country)
        ]
    else:
        data = gap

    if yr:
        data = data.loc[gap['year']==yr]

    return data

@app.callback(Output("bubble_chart", "srcDoc"), Input("yr", "value"))
def plot_bubble_chart(yr):
    """Create a bubble chart for income vs. life expectancy for a given year.

    Parameters
    ----------
    yr : int
        The year to filter for.

    Returns
    -------
    chart
        The bubble chart.
    """
    df = filter_year(yr)

    chart = (
        alt.Chart(df, title="Income vs. Life Expectancy")
        .mark_circle()
        .encode(
            alt.X(
                "log_income", title="Income (Log Scale)", scale=alt.Scale(zero=False)
            ),
            alt.Y(
                "life_expectancy",
                title="Life Expectancy (Years)",
                scale=alt.Scale(zero=False),
            ),
            alt.Size(
                "population", title="Population", scale=alt.Scale(range=(10, 1000))
            ),
            alt.Color("region", title="Continent"),
        )
        .configure_axis(titleFontSize=14)
    )

    return chart.to_html()

# Set up callbacks/backend
@app.callback(
    Output('barchart', 'srcDoc'),
    Input('yr', 'value'))

def plot_country(yr):

    """Create a bar chart for top 10 countries in terms of life expectancy.

    Parameters
    ----------
    yr : int
        The year to filter for.

    Returns
    -------
    chart
        The bar chart.
    """

    df = filter_year(yr)

    country = (
        alt.Chart(df, title='Top 10 Countries').mark_bar().encode(
            y=alt.Y('country', sort='-x', title='Country'),
            x=alt.X('life_expectancy', title='Life Expectancy'),
            color=alt.Color('life_expectancy')
        ).transform_window(
            rank='rank(life_expectancy)',
            sort=[alt.SortField('life_expectancy', order='descending')]
        ).transform_filter(
            (alt.datum.rank < 10))
    )

    return country.to_html()



if __name__ == '__main__':
    app.run_server(debug=True)
    