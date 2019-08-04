# Import required libraries
import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
from plotly import graph_objs as go
from colour import Color

# Multi-dropdown options
from controls import NEIGHBORHOODS

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

price_range_options = [
    {"label": price_range, "value": price_range}
    for price_range in ['$', '$$', '$$$', '$$$$', '$$$$$']]

well_type_options = [
    {"label": str(NEIGHBORHOODS[well_type]), "value": str(well_type)}
    for well_type in NEIGHBORHOODS
]

# Load data
df = pd.read_csv(DATA_PATH.joinpath("wellspublic.csv"), low_memory=False)
df["Date_Well_Completed"] = pd.to_datetime(df["Date_Well_Completed"])
df = df[df["Date_Well_Completed"] > dt.datetime(1960, 1, 1)]

trim = df[["API_WellNo", "Well_Type", "Well_Name"]]
trim.index = trim["API_WellNo"]
dataset = trim.to_dict(orient="index")

points = pickle.load(open(DATA_PATH.joinpath("points.pkl"), "rb"))

# Create global chart template
mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-79.41, lat=43.76),
        zoom=15,
    ),
)

# Create app layout
app.layout = html.Div(
    [
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("mit_logo.png"),
                            id="mit-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Bar Crawl Optimizer",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Solution Overview", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Learn More", id="learn-more-button"),
                            href="https://plot.ly/dash/pricing/",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [html.Div([
                        html.Div([
                            html.P(
                                "Select a date:",
                                className="control_label",
                            ),
                            html.Div(
                                dcc.DatePickerSingle(
                                    id='crawl_date',
                                    min_date_allowed=dt.datetime.today(),
                                    max_date_allowed=dt.datetime(2020, 9, 19),
                                    initial_visible_month=dt.datetime(2020, 8, 5),
                                    date=str(dt.datetime.today()))
                            ), ],
                            className="one-third column"),
                        html.Div([
                            html.P("Start time", className="control_label"),
                            dcc.Dropdown(
                                id='start_time',
                                options=[
                                    {'label': '12:00pm', 'value': '12'},
                                    {'label': '1:00pm', 'value': '13'},
                                    {'label': '2:00pm', 'value': '14'},
                                    {'label': '3:00pm', 'value': '15'},
                                    {'label': '4:00pm', 'value': '16'},
                                    {'label': '5:00pm', 'value': '17'},
                                    {'label': '6:00pm', 'value': '18'},
                                    {'label': '7:00pm', 'value': '19'},
                                    {'label': '8:00pm', 'value': '20'},
                                    {'label': '9:00pm', 'value': '21'},
                                    {'label': '10:00pm', 'value': '22'},
                                    {'label': '11:00pm', 'value': '23'},
                                    {'label': '12:00am', 'value': '0'},
                                    {'label': '1:00am', 'value': '1'},
                                    {'label': '2:00am', 'value': '2'}
                                ],
                            ), ], className="one-third column"),
                        html.Div([
                            html.P("End time", className="control_label"),
                            dcc.Dropdown(
                                id='end_time',
                                options=[
                                    {'label': '12:00pm', 'value': '12'},
                                    {'label': '1:00pm', 'value': '13'},
                                    {'label': '2:00pm', 'value': '14'},
                                    {'label': '3:00pm', 'value': '15'},
                                    {'label': '4:00pm', 'value': '16'},
                                    {'label': '5:00pm', 'value': '17'},
                                    {'label': '6:00pm', 'value': '18'},
                                    {'label': '7:00pm', 'value': '19'},
                                    {'label': '8:00pm', 'value': '20'},
                                    {'label': '9:00pm', 'value': '21'},
                                    {'label': '10:00pm', 'value': '22'},
                                    {'label': '11:00pm', 'value': '23'},
                                    {'label': '12:00am', 'value': '0'},
                                    {'label': '1:00am', 'value': '1'},
                                    {'label': '2:00am', 'value': '2'},
                                    {'label': '3:00am', 'value': '3'}
                                ],
                            ), ], className="one-third column"), ], className="row flex-display"),
                        html.P("Filter by budget range:", className="control_label"),
                        dcc.Dropdown(
                            id="well_statuses",
                            options=price_range_options,
                            multi=True,
                            value=[],
                            className="dcc_control",
                        ),
                        html.Div([
                            html.P("Number of bars", className="control_label"),
                            html.Div(
                                dcc.Slider(
                                    id='num_stops',
                                    min=0,
                                    max=10,
                                    value=5,
                                    marks={
                                        2: {'label': '2'},
                                        4: {'label': '4'},
                                        6: {'label': '6'},
                                        8: {'label': '8'},
                                        10: {'label': '10'},
                                    }
                                ))], className="one-half column"),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.P("Maximum total walking time", className="control_label"),
                        html.Div(dcc.Input(
                            id="max_walking_time",
                            type='text',
                            value=60,
                            placeholder='Max total walking time'
                        )),
                        html.P("Maximum walking time between each bar", className="control_label"),
                        html.Div(dcc.Input(
                            id="single_walking_time",
                            type='text',
                            value=15,
                            placeholder='Max walking time between each bar'
                        )),
                        html.P("Minimum number of reviews by bar", className="control_label"),
                        html.Div(dcc.Input(
                            id="min_review_ct",
                            type='text',
                            value=5,
                            placeholder='Min number of reviews by bar'
                        )),
                        html.P("Minimum bar review (from 0 to 5)", className="control_label"),
                        html.Div(dcc.Input(
                            id="min_review",
                            type='text',
                            value=3,
                            placeholder='Min bar review'
                        )),
                        html.Button('Go', id='go_button'),
                    ],
                    className="pretty_container six columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [html.Div(
                        [dcc.Graph(id="histogram")],
                        className="pretty_container nine columns",
                    ),
                        html.Div(
                            [
                                html.Div(
                                    [html.P("Total walking time"),
                                     #       id="walking_time_val",
                                     #       className="mini_container",
                                     html.Div(dcc.Input(
                                         id="walking_time",
                                         type='text',
                                         value=60
                                     )), ],
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.P("Combinations considered"),
                                     #       id="walking_time_val",
                                     #       className="mini_container",
                                     html.Div(dcc.Input(
                                         id="temp_val",
                                         type='text',
                                         value=60
                                     )), ],
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="oilText"), html.P("Average rating")],
                                    id="oil",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="waterText"), html.P("Estimated cost")],
                                    id="water",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),

                        #  html.Div(
                        #      [dcc.Graph(id="count_graph")],
                        #      id="countGraphContainer",
                        #      className="pretty_container",
                        #  ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="satellite_graph")],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="individual_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                # html.Div(
                #     [dcc.Graph(id="pie_graph")],
                #     className="pretty_container seven columns",
                # ),
                #  html.Div(
                #      [dcc.Graph(id="histogram")],
                #      className="pretty_container five columns",
                #  ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# Helper functions
def human_format(num):
    magnitude = 1  # int(math.log(num, 1000))
    mantissa = str(int(num / (1000 ** magnitude)))
    return mantissa + ["", "K", "M", "G", "T", "P"][magnitude]


def produce_individual(api_well_num):
    try:
        points[api_well_num]
    except:
        return None, None, None, None

    index = list(
        range(min(points[api_well_num].keys()), max(points[api_well_num].keys()) + 1)
    )
    gas = []
    oil = []
    water = []

    for year in index:
        try:
            gas.append(points[api_well_num][year]["Rating, stars"])
        except:
            gas.append(0)
        try:
            oil.append(points[api_well_num][year]["Price, $"])
        except:
            oil.append(0)
        try:
            water.append(points[api_well_num][year]["Distance walked, feet"])
        except:
            water.append(0)

    return index, gas, oil, water


def produce_aggregate(selected, hour_slider):
    index = list(range(max(hour_slider[0], 1985), 2016))
    gas = []
    oil = []
    water = []

    for year in index:
        count_gas = 0
        count_oil = 0
        count_water = 0
        for api_well_num in selected:
            try:
                count_gas += points[api_well_num][year]["Rating, stars"]
            except:
                pass
            try:
                count_oil += points[api_well_num][year]["Price, $"]
            except:
                pass
            try:
                count_water += points[api_well_num][year]["Distance walked, feet"]
            except:
                pass
        gas.append(count_gas)
        oil.append(count_oil)
        water.append(count_water)

    return index, gas, oil, water


# Selectors -> main graph
@app.callback(
    Output("satellite_graph", "figure"),
    [Input("walking_time", "value")]
)
def make_main_figure(walking_time):
    # dff = filter_dataframe(df, well_statuses, well_types, hour_slider)
    df = pd.read_csv('business.csv')
    df_bars = df[(df['categories'].str.contains('Bars')
                  | df['categories'].str.contains('Nightlife')
                  | df['categories'].str.contains('Pubs'))
                 & (~df['categories'].str.contains('Sushi Bars')
                    & ~df['categories'].str.contains('Juice Bars'))]
    dff = df_bars.loc[lambda f: f['city'] == 'Toronto'][:10]
    dff['rounded_review'] = round(dff['stars'],0)
    traces = []
    for name, dfff in dff.groupby("name"):
        trace = dict(
            type="scattermapbox",
            lon=dfff["longitude"],
            lat=dfff["latitude"],
            text=dfff['name'],
            customdata=dfff["rounded_review"],
            name=name,
            marker=dict(size=12, opacity=0.6),
        )
        traces.append(trace)

    layout = dict(
        autosize=True,
        automargin=True,
        margin=dict(l=30, r=30, b=20, t=40),
        hoverinfo="name",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        legend=dict(font=dict(size=10), orientation="h"),
        title="Satellite Overview",
        mapbox=dict(
            accesstoken=mapbox_access_token,
            style="light",
            center=dict(lon=dff['longitude'].mean(), lat=dff['latitude'].mean()),
            zoom=12,
        ),
    )

    figure = dict(data=traces, layout=layout)
    return figure

@app.callback(Output("temp_val", "value"),
              [Input("go_button", "n_clicks")],
              [State("num_stops", "value")])
def filter_dataframe(go, num_stops):
    #TODO: Call model from here
    return num_stops


# Main graph -> individual graph
@app.callback(Output("individual_graph", "figure"), [Input("satellite_graph", "hoverData")])
def make_individual_figure(main_graph_hover):
    layout_individual = copy.deepcopy(layout)

    if main_graph_hover is None:
        main_graph_hover = {
            "points": [
                {"curveNumber": 4, "pointNumber": 569, "customdata": 31101173130000}
            ]
        }

    chosen = [point["customdata"] for point in main_graph_hover["points"]]
    index, gas, oil, water = produce_individual(chosen[0])

    if index is None:
        annotation = dict(
            text="No data available",
            x=0.5,
            y=0.5,
            align="center",
            showarrow=False,
            xref="paper",
            yref="paper",
        )
        layout_individual["annotations"] = [annotation]
        data = []
    else:
        data = [
            dict(
                type="scatter",
                mode="lines+markers",
                name="Rating (mcf)",
                x=index,
                y=gas,
                line=dict(shape="spline", smoothing=2, width=1, color="#fac1b7"),
                marker=dict(symbol="diamond-open"),
            ),
            dict(
                type="scatter",
                mode="lines+markers",
                name="Price (bbl)",
                x=index,
                y=oil,
                line=dict(shape="spline", smoothing=2, width=1, color="#a9bb95"),
                marker=dict(symbol="diamond-open"),
            ),
            dict(
                type="scatter",
                mode="lines+markers",
                name="Water Produced (bbl)",
                x=index,
                y=water,
                line=dict(shape="spline", smoothing=2, width=1, color="#92d8d8"),
                marker=dict(symbol="diamond-open"),
            ),
        ]
        layout_individual["title"] = dataset[chosen[0]]["Well_Name"]

    figure = dict(data=data, layout=layout_individual)
    return figure


# Selected Data in the Histogram updates the Values in the DatePicker
@app.callback(
    Output("walking_time", "value"),
    [Input("histogram", "selectedData"), Input("histogram", "clickData")],
)
def update_bar_selector(value, clickData):
    if clickData:
        return str(clickData["points"][0]["x"])
    return ''


# Clear Selected Data if Click Data is used
@app.callback(Output("histogram", "selectedData"), [Input("histogram", "clickData")])
def update_selected_data(clickData):
    if clickData:
        return {"points": []}


# Update Histogram Figure based on Month, Day and Times Chosen
@app.callback(
    Output("histogram", "figure"),
    [
        Input("go_button", "n_clicks"),
        Input("histogram", "clickData")
    ],
    [
        State("walking_time", "value"),
        State("satellite_graph", "hoverData"),
    ],

)
def make_aggregate_figure(nclicks, clickdata, walking_distance, main_graph_hover):
    print(nclicks)
    if nclicks is None:
        return {}
    else:
        xVal = np.array([30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95])
        yVal = np.array([2.5, 3.2, 3.5, 3.8, 4.0, 4.2, 4.4, 4.6, 4.7, 4.8, 4.8, 4.8, 4.8, 4.8])

    colors = list(Color("blue").range_to(Color("green"), len(xVal)))

    if walking_distance != '':
        walking_distance = float(walking_distance)
        colors = [(255 * c.rgb[0], 255 * c.rgb[1], 255 * c.rgb[2], 0.2) for c in colors]
    else:
        colors = [(255 * c.rgb[0], 255 * c.rgb[1], 255 * c.rgb[2], 0.5) for c in colors]
    if walking_distance in xVal:
        c_selected = colors[np.where(xVal == walking_distance)[0][0]]
        colors[np.where(xVal == walking_distance)[0][0]] = (c_selected[0], c_selected[1], c_selected[2], 0.5)

    colors = ['rgba({},{},{},{})'.format(round(a, 0), round(b, 0), round(c, 0), d) for (a, b, c, d) in colors]
    layout = go.Layout(
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=40, r=40, t=30, b=50),
        showlegend=False,
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        dragmode="select",
        title="Select desired walking and waiting time / rating combination",
        font=dict(color="black"),
        xaxis=dict(
            title='Total time spent walking and waiting at bars (minutes)',
            range=[min(xVal), max(xVal)],
            showgrid=False,
            nticks=25,
            fixedrange=True,
            #  ticksuffix=":00",
        ),
        yaxis=dict(
            #   range=[0, max(yVal) + max(yVal) / 4],
            title='Average rating',
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            rangemode="nonnegative",
            zeroline=False,
        ),
        annotations=[
            dict(
                x=xi,
                y=yi,
                text=str(yi),
                xanchor="center",
                yanchor="bottom",
                showarrow=False,
                font=dict(color="black"),
            )
            for xi, yi in zip(xVal, yVal)
        ],
    )

    return go.Figure(
        data=[
            go.Bar(x=xVal, y=yVal, marker=dict(color=colors),
                   hoverinfo="x"),
            go.Scatter(
                opacity=0,
                x=xVal,
                y=yVal,
                hoverinfo="none",
                mode="markers",
                marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
                visible=True,
            ),
        ],
        layout=layout,
    )


# Main
if __name__ == "__main__":
    app.run_server(debug=True)
