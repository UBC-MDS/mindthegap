from dash import Dash, html, dcc, Input, Output
import pandas as pd
import altair as alt
from vega_datasets import data



app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server=app.server

#dictionary to generate dynamic metrics in altair
metrics={'life_expectancy':'Life Expectancy', 'child_mortality':'Child Mortality', 'pop_density':'Population Density'}

#merge country_id.csv with gaominder.csv
gap = pd.read_csv('data/gapminder.csv')
country_ids=pd.read_csv('data/country_ids.csv')
gap = gap.merge(country_ids, how="outer", on=["country"])

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
    html.Iframe(id='map',
                style={'border-width': '0', 'width': '100%', 'height': '600px'})
 
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
    