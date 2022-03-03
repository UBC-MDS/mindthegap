from dash import Dash, html, dcc, Input, Output
import numpy as np
import pandas as pd
import altair as alt
from vega_datasets import data
import dash_bootstrap_components as dbc
import os
# Current Path
current_dir = os.path.abspath(os.path.dirname(__file__))

app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server=app.server

#dictionary to generate dynamic metrics in altair
metrics={'life_expectancy':'Life Expectancy', 'child_mortality':'Child Mortality', 'pop_density':'Population Density'}

#merge country_id.csv with gaominder.csv'
gap = pd.read_csv(os.path.join(current_dir, '../data/gapminder.csv'))
country_ids=pd.read_csv(os.path.join(current_dir, '../data/country_ids.csv'))
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

worldmap = html.Iframe(
    id="worldmap",
    style={
         "border-width": "0",
        "width": "100%",
        "height": "400px"
    }
)

@app.callback(
    Output("sub_region", "options"),
    Input("region", "value"),
)
def get_sub_region(region):
    if region is None:
        options = [{"label": sub_region, "value": sub_region} for sub_region in gap["sub_region"].dropna().unique()]
    else:
        sub_regions = list(gap[gap['region']==region]['sub_region'].unique())
        options=[]
        for sr in sub_regions:
            options.append({"label":sr, "value":sr})
    return options

app.layout = html.Div([
    
    dcc.RadioItems(id='metric', value='life_expectancy',
        options=[{'label': v, 'value': k} for k, v in metrics.items()]),

    # adding the slider instead to filter year
    html.H3('Year'),
    html.P('The user can slide over the years to filter the year'),
    dcc.Slider(
        min=1970,
        max=2010,
        step=5,
        value=2010,
        id='yr',
        marks={i: str(i) for i in range(1970, 2015, 5)},
        ),
    # html.Br(),
    # 'Year',
    # dcc.Dropdown(id='yr', 
    #     options=[
    #             {'label': 1990, 'value': 1990},
    #             {'label': 2000, 'value': 2000},
    #             {'label': 2012, 'value': 2012},
    #             {'label': 2015, 'value': 2015}
    #             ],
    #         value=2012) ,
    # html.Br(),
    html.H3('Region'),
    dcc.Dropdown(id='region', 
        options=[{"label": reg, "value": reg} for reg in gap["region"].dropna().unique()],
        value=None
        ),
    html.H3('Sub Region'),
    dcc.Dropdown(id='sub_region',
        # options=None,
        value=None) ,
    # html.H3('Country'),
    # dcc.Dropdown(id='country',
    #     value=None),
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
    Input("region", "value"),
    Input("sub_region", "value"),
    Input("yr", "value"),
)
def plot_box_plot(metric, region, sub_region, yr):
    """
    Create box chart for statsitic of interested based on selected filters for income groups
    Parameters
    --------
    metric: string
        Selection from statistic of interest filter
    region: string
        Selection from the region filter
    sub_region: sting
        Selection from Sub Region filter
    year: integer
        Year for which the data is displayed, from Year filter
    Returns
    --------
    chart
        bar chart showing statistic of interest for income groups,
        in specific region, subregion and year
    Example
    --------
    > plot_box_plot("child_mortality", "Asia", "Western Asia", None, 2015)
    """
    alt.data_transformers.disable_max_rows()

    # filter by region, sub-region & year
    data = filter_data(region, sub_region, None, yr)
    
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
    Filter data based on region, sub region and country selection
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
        dataset that has been filtered on region, sub region and country selection
    Example
    --------
    > filter_data(d"Asia", "Western Asia", "Yemen", 2015)
    """
    # Filter by region, sub-region, country
    if country:
        data = gap.query(f"country == '{country}'")
    elif sub_region:
        data = gap.query(f"sub_region == '{sub_region}'")
    elif region:
        data = gap.query(f"region == '{region}'")
    else:
        data = gap
    # Filter by year
    if yr:
        data = data.query(f"year == {yr}")

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
    Input("metric", "value"),
    Input("region", "value"),
    Input("sub_region", "value"),
    Input("yr", "value"),
)

def plot_country(metric, region, sub_region, yr):

    """Create a bar chart for top 10 countries in terms of life expectancy.

    Parameters
    ----------
    metric: string
        Selection from statistic of interest filter
    region: string
        Selection from the region filter
    sub_region: string
        Selection from Sub Region filter
    yr : int
        The year to filter for.

    Returns
    -------
    chart
        The bar chart that shows top 10 countries for filters selected
    """

    data = filter_data(region, sub_region, None, yr)

    country = (
        alt.Chart(data, title=f"{metrics[metric]} - Top 10 Country for Year {yr}")
        .mark_bar().encode(
            y=alt.Y('country', sort='-x', title='Country'),
            x=alt.X(metric, title=metrics[metric]),
            color=alt.Color(metric + ":Q", title=metrics[metric])
        ).transform_window(
            rank='rank(life_expectancy)',
            sort=[alt.SortField(metric, order='descending')]
        ).transform_filter(
            (alt.datum.rank < 10))
    )

    return country.to_html()



if __name__ == '__main__':
    app.run_server(debug=True)
    