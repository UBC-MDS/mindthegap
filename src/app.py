from dash import Dash, html, dcc, Input, Output
import numpy as np
import pandas as pd
import altair as alt
from vega_datasets import data
import dash_bootstrap_components as dbc
import os


app = Dash(
    __name__, title="Mindthegap Dashboard", external_stylesheets=[dbc.themes.BOOTSTRAP]
)
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
FILTER_STYLE = {"background-color": "#f8f9fa", "width": "18rem", "height": "100%"}

filter_panel = dbc.Card(
    dbc.Col(
        [
            html.Br(),
            html.Br(),
            
            html.Br(),
            # control panel title
            html.H2("Control Panel", className="text-center"),
            html.Br(),
            html.Br(),
            # metric radio button
            dbc.Row(
                [
                    html.H5("1.  Metric", className="text-left"),
                    dbc.RadioItems(
                        id="metric",
                        value="life_expectancy",
                        labelStyle={"display": "block"},
                        options=[{"label": v, "value": k} for k, v in metrics.items()],
                    ),
                ]
            ),
            html.Br(),
            html.Br(),
            # continent drop down
            dbc.Row(
                [
                    html.H5("2.  Continent", className="text-left"),
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
            html.Br(),
            # sub-region drop down
            dbc.Row(
                [
                    html.H5("3.  Sub Continent", className="text-left"),
                    dcc.Dropdown(id="sub_region", value=None),
                ]
            ),
            html.Br(),
            html.Br(),
            
            html.Br(),
            html.Br(),
            
            html.Br(),
            dbc.Row(
                [
                    html.H5("Data Source", className="text-left"),
                    dcc.Markdown("""Dataset for visualization of this dashbaord can be downloaded from [here](https://github.com/UBC-MDS/mindthegap/blob/main/data/gapminder.csv)
            """
            ),
                ]
            ),
            html.Br(),
            html.Br(),
            html.P("Note: If a plot is empty, this means that there is no data based on your selections.")
            
            
            
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
    id="worldmap", 
    style={"border-width": "4px", "width": "100%", "min-height": "400px"}
)

############################## DASHBOARD LAYOUT ###################################
app.layout = dbc.Container(
    [
        # title
        html.Div(
            style={"textAlign": "center", "color": "black", "font-size": "26px"},
            children=[
                html.H1("Mindthegap Dashboard"),
            ],
        ),
        html.Br(),
        dbc.Row(
            [
                # control panel
                dbc.Col(filter_panel, md=5, lg=3, sm=3),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H5("Select Year", className="text-left"),
                                        dcc.Slider(
                                            min=1970,
                                            max=2010,
                                            step=5,
                                            value=2010,
                                            id="yr",
                                            marks={
                                                str(i): {
                                                    "label": str(i),
                                                    "style": {"color": "black"},
                                                }
                                                for i in range(1970, 2015, 5)
                                            },
                                        ),
                                    ],
                                    md=10, lg=10
                                ),
                                dbc.Row(),
                                html.Br(),
                                dbc.Row([
            html.H5("World Map view by Metric", style={"width": "fit-content"}),
            dbc.Col(
                        [
                            dbc.Button(
                                id="map_tooltip",
                                color="secondary",
                                children=html.Strong("?"),
                                size="sm",
                                outline=True,
                            ),
                            dbc.Tooltip(
                                "Choose metric from the control panel, drag and select the year to view the change of metric in the world using the slide bar. Select a continent to view a zoomed version of continent. You can hover over the plot for more details",
                                target="map_tooltip",
                                placement="bottom",
                            ),
                        ]                    )
        ], style={"padding": "3vh 0"}),
                                    
                                    
                                    

                                dbc.Col([
                                    dbc.Card(
                                        dbc.Col(

                                        dbc.Row(
                                            [dbc.Col(
                                                [
                                                    worldmap
                                                    ], 
                                                    md=10, lg=12,
                                                    ),
                                                    ]
                                                    ), 
                                                    ),
                                        
                                                    style={"border":"0px"}),
                                            html.Br(),
                                            html.Br(),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Row([
            html.H5("Top/Bottom countries by Metric", style={"width": "fit-content"}),
            dbc.Col(
                        [
                            dbc.Button(
                                id="bar_tooltip",
                                color="secondary",
                                children=html.Strong("?"),
                                size="sm",
                                outline=True,
                            ),
                            dbc.Tooltip(
                                "Choose metric from the control panel, drag and select the year using the slide bar. Select a continent and/or sub-continent to view the top/bottom countries for that metric",
                                target="bar_tooltip",
                                placement="bottom",
                            ),
                        ]                    )
        ], style={"padding": "3vh 0"}),
                                                    dbc.Card([
                                                        dbc.Card(
                                                            html.Div(
                                                                [
                                                                    # dbc.Label("Choose Top/Bottom by country"),
                                                                    dbc.RadioItems(
                                                                        options=[
                                                                            {"label": "Top Countries", "value": "Top"},
                                                                            {"label": "Bottom Countries", "value": "Bottom"},
                                                                        ],
                                                                        value="Top",
                                                                        id="radio",
                                                                        inline=True,
                                                                        style={"align":"center"},
                                                                        labelStyle={"align":"center"}
                                                                    ),
                                                                    
                                                                ]
                                                            ),
                                                            style={"height":"43px"}
                                                        ),
                                                        

                                                        html.Div(barchart)
                                                    ])
                                                    ], 
                                                    md=6,lg=6
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Row([
            html.H5("GDP/Income by Metric", style={"width": "fit-content"}),
            dbc.Col(
                        [
                            dbc.Button(
                                id="tab_tooltip",
                                color="secondary",
                                children=html.Strong("?"),
                                size="sm",
                                outline=True,
                            ),
                            dbc.Tooltip(
                                "Choose metric from the control panel, drag and select the year using the slide bar. Select a continent and/or sub continent to view the changes in GDP w.r.t to population size and the changes in income by the parameters selected. You can hover over regions on the map",
                                target="tab_tooltip",
                                placement="bottom",
                            ),
                        ]                    )
        ], style={"padding": "3vh 0"}),
                                                        dbc.Card([
                                                        html.Div(
                                                            dbc.Tabs(
                                                                id="tabs",
                                                                active_tab="gdp",
                                                                children=[
                                                                    dbc.Tab(
                                                                        label="GDP",
                                                                        tab_id="gdp",
                                                                    ),
                                                                    dbc.Tab(
                                                                        label="Income",
                                                                        tab_id="income",
                                                                    ),
                                                                ],
                                                            ),
                                                        ),
                                                        html.Div(id="tab-content")
                                                        ])
                                                        ],
                                                md=6, lg=6),
                                            ]
                                        ),
                                    ],
                                    md=10, lg=10
                                ),
                            ]
                        )
                    ]
                ),
            ]
        ),
    ],
    fluid=True,
)

############################## HELPER FUNCTIONS ###################################
@app.callback(Output("tab-content", "children"), Input("tabs", "active_tab"))
def render_graph(tabs):
    if tabs == "gdp":
        return html.Div([bubblechart])
    elif tabs == "income":
        return html.Div([boxplot])


def filter_data(region, sub_region, country, yr):
    """
    Filter data based on region, sub region and country selection
    Parameters
    --------
    region: string
        Selection from the Region filter
    sub_region: string
        Selection from Sub Region filter
    country: string
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

    @app.callback(
        Output("country", "options"),
        Input("region", "value"),
        Input("sub_region", "value"),
    )
    def get_country(region, sub_region):

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
        options = [
            {"label": cntry, "value": cntry}
            for cntry in gap["country"].dropna().unique()
        ]

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
                lookup="id",
                from_=alt.LookupData(df, key="id", fields=["country", metric]),
            )
            .encode(
                tooltip=["country:O", metric + ":Q"],
                color=alt.Color(metric + ":Q", title=metrics[metric]),
            )
            .properties(width=750, height=350)
        )

    else:
        scl = None
        trans = None
        if region == "Europe":
            scl = 800
            trans = [150, 1010]
        elif region == "Asia":
            scl = 500
            trans = [-100, 500]
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
                lookup="id",
                from_=alt.LookupData(df, key="id", fields=["country", metric]),
            )
            .encode(
                tooltip=["country:O", metric + ":Q"],
                color=alt.Color(metric + ":Q", title=metrics[metric]),
            )
            .project(type="naturalEarth1", scale=scl, translate=trans)
            .properties(width=750, height=350)
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
    sub_region: string
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
            title=f"{metrics[metric]} by Income Group for year {yr}",
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
        .properties(width=450, height=300)
        .configure_legend(gradientLength=900, gradientThickness=400)

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
    sub_region: string
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

    if region is not None and sub_region is None:
        chart = (
            (
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
                        "population",
                        title="Population",
                        scale=alt.Scale(range=(10, 1000)),
                    ),
                    alt.Color("sub_region", title="Sub Continent"),
                    tooltip=[
                        alt.Tooltip("region", title="Continent"),
                        alt.Tooltip("sub_region", title="Sub region"),
                        alt.Tooltip("country", title="Country"),
                        alt.Tooltip(metric, title=metrics[metric]),
                        alt.Tooltip("income", title="GDP per Capita", format=","),
                    ],
                )
                .configure_axis(titleFontSize=14)
            )
            .properties(width=420, height=300)
            # .configure_legend(gradientLength=900, gradientThickness=400)
        )

    elif region is None and sub_region is None:
        chart = (
            (
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
                        "population",
                        title="Population",
                        scale=alt.Scale(range=(10, 1000)),
                    ),
                    alt.Color("region", title="Continent"),
                    tooltip=[
                        alt.Tooltip("region", title="Continent"),
                        alt.Tooltip("sub_region", title="Sub region"),
                        alt.Tooltip("country", title="Country"),
                        alt.Tooltip(metric, title=metrics[metric]),
                        alt.Tooltip("income", title="GDP per Capita", format=","),
                    ],
                )
                .configure_axis(titleFontSize=14)
            )
            .properties(width=300, height=300)
            .configure_legend(gradientLength=900, gradientThickness=400)
        )
    elif region is not None and sub_region is not None:
        chart = (
            (
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
                        "population",
                        title="Population",
                        scale=alt.Scale(range=(10, 1000)),
                    ),
                    alt.Color("country", title="Country"),
                    tooltip=[
                        alt.Tooltip("region", title="Continent"),
                        alt.Tooltip("sub_region", title="Sub region"),
                        alt.Tooltip("country", title="Country"),
                        alt.Tooltip(metric, title=metrics[metric]),
                        alt.Tooltip("income", title="GDP per Capita", format=","),
                    ],
                )
                .configure_axis(titleFontSize=14)
            )
            .properties(width=300, height=300)
            .configure_legend(gradientLength=900, gradientThickness=400)
        )

    return chart.to_html()


@app.callback(
    Output("barchart", "srcDoc"),
    Input("metric", "value"),
    Input("region", "value"),
    Input("radio", "value"),
    Input("sub_region", "value"),
    Input("yr", "value"),
)
def plot_bar_chart(metric, region, radio, sub_region, yr):
    """
    Create a bar chart for top 10 countries in terms of life expectancy.
    Parameters
    --------
    metric: string
        Selection from statistic of interest filter
    region: string
        Selection from the region filter
    radio: int
        Selection of radio button as Top or Bottom
    sub_region: string
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
    if radio == "Top":
        order="descending"
    else:
        order="ascending"
    country = (
        alt.Chart(data, title=f"{metrics[metric]} - {radio} 10 Countries for Year {yr}")
        .mark_bar()
        .encode(
            y=alt.Y("country", sort="-x", title="Country"),
            x=alt.X(metric, title=metrics[metric]),
            color=alt.Color(metric + ":Q", title=metrics[metric]),
            tooltip=("country:O", metric + ":Q")
        )
        .transform_window(
            rank="rank(life_expectancy)",
            sort=[alt.SortField(metric, order=order)],
        )
        .transform_filter((alt.datum.rank < 10))
    ).properties(width=410, height=300)


    return country.to_html()


if __name__ == "__main__":
    app.run_server(debug=os.environ.get("IS_DEBUG", False))
