from dash import Dash, html, dcc, Input, Output
import numpy as np
import pandas as pd
import altair as alt
from vega_datasets import data
import dash_bootstrap_components as dbc
import os


app = Dash(__name__, title="Mindthegap Dashboard", external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# read in gapminder and continent data
current_dir = os.path.abspath(os.path.dirname(__file__))
country_ids = pd.read_csv(os.path.join(current_dir, "../data/country_ids.csv"))
gap = pd.read_csv(os.path.join(current_dir, "../data/gapminder.csv"))
gap = gap.merge(country_ids, how="outer", on=["country"])
gap["log_income"] = gap["income"].apply(np.log)

# dictionary to generate dynamic metrics in altair
metrics = {
    "life_expectancy": "Life Expectancy",
    "child_mortality": "Child Mortality",
    "pop_density": "Population Density",
}

############################## CONTROL PANEL FILTERS ##############################
FILTER_STYLE = {"background-color": "#f8f9fa"}

filter_panel = dbc.Card(
    dbc.Col(
        [
            # control panel title
            html.H2("Control Panel", className="text-center"),
            html.Br(),
            # metric radio button
            dbc.Row(
                [
                    html.H5("1. Metric", className="text-left"),
                    dbc.RadioItems(
                        id="metric",
                        value="life_expectancy",
                        labelStyle={"display": "block"},
                        options=[{"label": v, "value": k} for k, v in metrics.items()],
                    ),
                ]
            ),
            html.Br(),
            # continent drop down
            dbc.Row(
                [
                    html.H5("2. Continent", className="text-left"),
                    dcc.Dropdown(
                        id="region",
                        options=[
                            {"label": reg, "value": reg}
                            for reg in gap["region"].dropna().unique()
                        ],
                        value=None,
                    ),
                ]
            ),
            html.Br(),
            # sub-region drop down
            dbc.Row(
                [
                    html.H5("3. Sub Region", className="text-left"),
                    dcc.Dropdown(id="sub_region", value=None),
                ]
            ),
            html.Br(),
            # year slider
            dbc.Row(
                [
                    html.H5("4. Year", className="text-left"),
                    dcc.Slider(
                        min=1970,
                        max=2010,
                        step=5,
                        value=2010,
                        id="yr",
                        marks={
                            str(i): {"label": str(i), "style": {"color": "black"}}
                            for i in range(1970, 2015, 5)
                        },
                    ),
                ]
            ),
            html.Br(),
            # empty plot message
            html.Small(
                "Note: If a plot is empty, this means that there is no data based on your selections."
            ),
        ],
    ),
    style=FILTER_STYLE,
    body=True,
)

############################## PLOT OBJECTS #######################################
boxplot = html.Iframe(
    id="boxplot",
    style={"border-width": "0", "width": "100%", "min-height": "400px"},
)

bubblechart = html.Iframe(
    id="bubblechart",
    style={"border-width": "0", "width": "100%", "height": "400px"},
)

barchart = html.Iframe(
    id="barchart",
    style={
        "border-width": "0",
        "width": "100%",
        "height": "400px",
    },
)

worldmap = html.Iframe(
    id="worldmap", style={"border-width": "0", "width": "100%", "min-height": "400px"}
)

############################## DASHBOARD LAYOUT ###################################
app.layout = dbc.Container(
    [
        # title
        html.Div(
            style={"textAlign": "center", "color": "Gray", "font-size": "26px"},
            children=[
                html.H1("Mindthegap Dashboard"),
            ],
        ),
        html.Br(),
        dbc.Row(
            [
                # control panel
                dbc.Col(filter_panel, md=3),
                # grid of 4 plots
                dbc.Col(
                    [
                        dbc.Row([dbc.Col(worldmap, md=6), dbc.Col(boxplot, md=6)]),
                        dbc.Row([dbc.Col(barchart, md=6), dbc.Col(bubblechart, md=6)]),
                    ],
                    md=9,
                ),
            ]
        ),
    ],
    fluid=True,
)

############################## HELPER FUNCTIONS ###################################

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
    > filter_data("Asia", "Western Asia", "Yemen", 2015)
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


@app.callback(
    Output("sub_region", "options"),
    Input("region", "value"),
)
def get_sub_region(region):
    """Get a sub region value(s) based on a region value in gapminder
    Parameters
    ----------
    region : string
        The region to get subregions for
    Returns
    -------
    options
        Dict of subregion label/values
    """
    if region is None:
        options = [
            {"label": sub_region, "value": sub_region}
            for sub_region in gap["sub_region"].dropna().unique()
        ]
    else:
        sub_regions = list(gap[gap["region"] == region]["sub_region"].unique())
        options = []
        for sr in sub_regions:
            options.append({"label": sr, "value": sr})
    return options


############################## PLOTTING FUNCTIONS #################################
@app.callback(
    Output("worldmap", "srcDoc"),
    Input("metric", "value"),
    Input("region", "value"),
    Input("yr", "value"),
)
def plot_world_map(metric, region, yr):
    """
    Create world heatmap for statsitic of interest based on selected year filter.
    Parameters
    --------
    metric: string
        Selection from statistic of interest filter
    yr: integer
        Year for which the data is displayed, from Year filter
    Returns
    --------
    chart
        World heatmap for statistic of interest based on year filter
    Example
    --------
    > plot_world_map("child_mortality", "Asia", 2015)
    """
    world = data.world_110m()
    world_map = alt.topo_feature(data.world_110m.url, "countries")
    alt.data_transformers.disable_max_rows()
    df = filter_data(region, None, None, yr)

    if region is None:

        chart = (
            alt.Chart(world_map, title=f"{metrics[metric]} by country for year {yr}")
            .mark_geoshape(stroke="black")
            .transform_lookup(
                lookup="id", from_=alt.LookupData(df, key="id", fields=["country", metric])
            )
            .encode(
                tooltip=["country:O", metric + ":Q"],
                color=alt.Color(metric + ":Q", title=metrics[metric]),
            )
           .properties(width=600, height=350)
        )

    else:
        scl = None
        trans = None
        if region == "Europe":
            scl = 800
            trans = [150, 1010]
        elif region == "Asia":
            scl = 500
            trans = [-200, 500]
        elif region == "Africa":
            scl = 500
            trans = [400, 300]
        elif region == "Americas":
            scl = 300
            trans = [1000, 350]
        elif region == "Oceania":
            scl = 500
            trans = [-400, 0]
        chart = (
            alt.Chart(world_map, title=f"{metrics[metric]} by country for year {yr}")
            .mark_geoshape(stroke="black")
            .transform_lookup(
                lookup="id", from_=alt.LookupData(df, key="id", fields=["country", metric])
            )
            .encode(
                tooltip=["country:O", metric + ":Q"],
                color=alt.Color(metric + ":Q", title=metrics[metric]))
            .project(type='naturalEarth1', scale=scl, translate=trans)
        .properties(width=600, height=350)
    )
    return chart.to_html()


@app.callback(
    Output("boxplot", "srcDoc"),
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
        Selection from sub region filter
    yr: integer
        Year for which the data is displayed, from Year filter
    Returns
    --------
    chart
        Bar chart showing statistic of interest for income groups,
        in specific region, subregion and year
    Example
    --------
    > plot_box_plot("child_mortality", "Asia", "Western Asia", 2015)
    """
    alt.data_transformers.disable_max_rows()

    # filter by region, sub-region & year
    data = filter_data(region, sub_region, None, yr)

    data = data[data["income_group"].notnull()]

    chart = (
        alt.Chart(
            data,
            title=f"{metrics[metric]} group by Income Group for year {yr}",
        )
        .mark_boxplot(size=50)
        .encode(
            alt.X("income_group", sort="-x", title="Income Group"),
            alt.Y(metric, title=metrics[metric], scale=alt.Scale(zero=False)),
            color=alt.Color(
                "income_group",
                sort=alt.EncodingSortField("income_group", order="descending"),
                title="Income Group",
            ),
            tooltip=("name:O", "child_mortality:Q"),
        )
        .configure_axis(labelFontSize=12, titleFontSize=14)
        .configure_legend(labelFontSize=12)
        .properties(width=250, height=350)
    )
    return chart.to_html()


@app.callback(
    Output("bubblechart", "srcDoc"),
    Input("metric", "value"),
    Input("region", "value"),
    Input("sub_region", "value"),
    Input("yr", "value"),
)
def plot_bubble_chart(metric, region, sub_region, yr):
    """
    Create bubble chart for statsitic of interested based on selected filters vs GDP
    Parameters
    --------
    metric: string
        Selection from statistic of interest filter
    region: string
        Selection from the region filter
    sub_region: sting
        Selection from sub region filter
    yr: integer
        Year for which the data is displayed, from Year filter
    Returns
    --------
    chart
        Bubble chart showing statistic of interest for income groups,
        in specific region, subregion and year vs GDP.
    Example
    --------
    > plot_bubble_chart("child_mortality", "Asia", "Western Asia", 2015)
    """
    df = filter_data(region, sub_region, None, yr)

    chart = (
        alt.Chart(df, title=f"{metrics[metric]} vs. GDP per Capita ($USD)")
        .mark_circle()
        .encode(
            alt.X(
                "log_income",
                title="GDP per Capita ($USD Log Scale)",
                scale=alt.Scale(zero=False),
            ),
            alt.Y(
                metric,
                title=metrics[metric],
                scale=alt.Scale(zero=False),
            ),
            alt.Size(
                "population", title="Population", scale=alt.Scale(range=(10, 1000))
            ),
            alt.Color("region", title="Continent"),
        )
        .configure_axis(titleFontSize=14)
    ).properties(width=500, height=300)

    return chart.to_html()


@app.callback(
    Output("barchart", "srcDoc"),
    Input("metric", "value"),
    Input("region", "value"),
    Input("sub_region", "value"),
    Input("yr", "value"),
)
def plot_bar_chart(metric, region, sub_region, yr):
    """
    Create a bar chart for top 10 countries in terms of life expectancy.
    Parameters
    --------
    metric: string
        Selection from statistic of interest filter
    region: string
        Selection from the region filter
    sub_region: sting
        Selection from sub region filter
    yr: integer
        Year for which the data is displayed, from Year filter
    Returns
    -------
    chart
        The bar chart that shows top 10 countries for filters selected
    Example
    --------
    > plot_bar_chart("child_mortality", "Asia", "Western Asia", 2015)
    """
    data = filter_data(region, sub_region, None, yr)

    country = (
        alt.Chart(data, title=f"{metrics[metric]} - Top 10 Country for Year {yr}")
        .mark_bar()
        .encode(
            y=alt.Y("country", sort="-x", title="Country"),
            x=alt.X(metric, title=metrics[metric]),
            color=alt.Color(metric + ":Q", title=metrics[metric]),
        )
        .transform_window(
            rank="rank(life_expectancy)",
            sort=[alt.SortField(metric, order="descending")],
        )
        .transform_filter((alt.datum.rank < 10))
    ).properties(width=500, height=300)

    return country.to_html()


if __name__ == "__main__":
    app.run_server(debug=os.environ.get("IS_DEBUG", False))