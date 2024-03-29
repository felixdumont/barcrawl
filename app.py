# Import required libraries

import pickle
from dateutil import parser
import requests
import config
import copy
import shutil
import os
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
from models.models import crawl_model
from models.clustering import get_clusters
import dash_daq as daq

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

app.config['suppress_callback_exceptions'] = True

price_range_options = [
    {"label": price_range, "value": len(price_range)}
    for price_range in ['$', '$$', '$$$', '$$$$', '$$$$$']]

points = pickle.load(open(DATA_PATH.joinpath("points.pkl"), "rb"))

# Create global chart template
mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"

layout = dict(
    autosize=False,
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
        zoom=18,
    ),
)

# Create app layout
app.layout = html.Div(
    [
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div([
            html.Div([
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div([
                                    html.Img(
                                        src=app.get_asset_url("mit_logo.png"),
                                        id="mit-image",
                                        style={
                                            "height": "60px",
                                            "width": "auto",
                                            "margin-bottom": "25px",
                                        }, className="plotly-logo"
                                    ), ], className='eight columns'),
                                html.Div([
                                    html.Img(
                                        src=app.get_asset_url("yelp_logo.png"),
                                        id="yelp-image",
                                        style={
                                            "height": "60px",
                                            "width": "auto",
                                            "margin-bottom": "25px",
                                            "margin-right": "0px",
                                            "text-align": "right"
                                        }, className="plotly-logo"

                                    ), ], className='four columns'),
                            ],
                            className="mobile_forms",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div([
                                            html.H1(
                                                "Bar Crawl Optimizer",
                                                style={"margin-bottom": "0px"},
                                            ), ], className='seven columns'),
                                        html.Div([
                                            html.A(
                                                html.Button("Learn More", id="learn-more-button"),

                                                style={"margin-left": "0px", "margin-right": "0px"},
                                                href="https://en.wikipedia.org/wiki/Pub_crawl",
                                            )
                                        ], className='demo_container')
                                    ]
                                )
                            ],
                            className="mobile_forms",
                            id="title",
                        ),
                    ],
                    id="header",
                    className="mobile_forms",
                    style={"margin-bottom": "25px"},
                ), html.Div(
                    [
                        html.Div(
                            [html.Div([
                                html.Div([
                                    html.Div(children=[
                                        html.Label(
                                            "Select a date:"
                                        ),
                                    ], className="eight columns", hidden=True),
                                ], className="mobile_forms", hidden=True),
                                html.Div([
                                    html.Div([
                                        html.Label("Enter a start address (optional):"),
                                        dcc.Textarea(id="address",
                                                     value="686 Queen St W, Toronto, ON M6J 1E7, Canada"),
                                    ], className="mobile_forms"),
                                    html.Div([
                                        html.Label(
                                            "Select a date:"
                                        ),
                                        dcc.DatePickerSingle(
                                            id='crawl_date',
                                            min_date_allowed=dt.datetime.today(),
                                            # with_portal=True,
                                            # max_date_allowed=dt.datetime(2020, 9, 19),
                                            # initial_visible_month=dt.datetime(2020, 8, 5),
                                            date=str(dt.datetime.today()))
                                    ], className="eight columns"),
                                    html.Div([
                                        html.Label("Start time"),
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
                                        ), ], className="six columns"),
                                    html.Div([
                                        html.Label("End time"),
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
                                        ), ], className="six columns"),
                                ], className="eight columns"),
                                html.Div([
                                    html.Label("Filter by budget range:"),
                                    dcc.Dropdown(
                                        id="budget_range",
                                        options=price_range_options,
                                        multi=True,
                                        value=[1, 2, 3, 4, 5],
                                        className="dcc_control",
                                    ), ], className="eight columns"),
                                html.Div([
                                    html.Label("Number of bars"),
                                    html.Div(
                                        dcc.Slider(
                                            id='num_stops',
                                            min=0,
                                            max=8,
                                            value=5,
                                            marks={
                                                2: {'label': '2'},
                                                4: {'label': '4'},
                                                6: {'label': '6'},
                                                8: {'label': '8'},
                                            }
                                        ))], className="eight columns"),
                                html.Div([
                                    html.Div([
                                        html.Label("Max total walking time"),
                                        html.Div(dcc.Input(
                                            id="max_walking_time",
                                            type='text',
                                            value=30,
                                            placeholder='Max total walking time'
                                        )), ], className="six columns"),
                                    html.Div([
                                        html.Label("Max total waiting time"),
                                        html.Div(dcc.Input(
                                            id="max_waiting_time",
                                            type='text',
                                            value=30,
                                            placeholder='Max total waiting time'
                                        )), ], className="six columns"),
                                    html.Div([
                                        html.Label("Max walking time between each bar"),
                                        html.Div(dcc.Input(
                                            id="single_walking_time",
                                            type='text',
                                            value=15,
                                            placeholder='Max walking time between each bar'
                                        )), ], className="six columns"),
                                ], className="eleven columns"),
                                html.Div([
                                    html.Div([
                                        html.Label("Min number of reviews by bar"),
                                        html.Div(dcc.Input(
                                            id="min_review_ct",
                                            type='text',
                                            value=20,
                                            placeholder='Min number of reviews by bar'
                                        )), ], className="six columns"),
                                    html.Div([
                                        html.Label("Min bar review (from 0 to 5)"),
                                        html.Div(dcc.Input(
                                            id="min_review",
                                            type='text',
                                            value=3.0,
                                            placeholder='Min bar review'
                                        )), ], className="six columns"),
                                    html.Div([
                                        html.Label("Use unsupervised learning?"),
                                        html.Div(
                                            daq.ToggleSwitch(
                                                id="unsupervised",
                                                value=False,
                                                color="#407DFA",
                                            ),
                                        ),
                                ], className="six columns"),
                                ], className="eleven columns"),

                                html.Div([
                                    html.Br(),
                                    html.Button('Apply filters', id='apply_button', className="button_submit"),
                                ], className="eight columns")
                            ], className="mobile_forms"),
                            ],
                            className="mobile_forms",
                            id="cross-filter-options",
                        ),
                        html.Div([], hidden=True),
                    ],
                    id="right-column",
                    className="mobile_forms",
                ),
            ], className="four columns instruction",
            ),

            html.Div(
                [
                    html.Div([
                        html.Label("Total walking time"),
                        html.Div(dcc.Input(
                            id="walking_time",
                            type='text',
                            value=60
                        )), ],
                        className="mini_container", hidden=True
                    ),
                    dcc.Tabs(
                        id="crawl-tabs",
                        value="tab-one",
                        children=[
                            dcc.Tab(label="INSTRUCTIONS", value="tab-one"),
                            dcc.Tab(label="SELECT DESIRED TRADEOFFS", value="tab-two"),
                            dcc.Tab(label="VIEW CRAWL", value="tab-three"),
                        ],
                        className="tabs",
                    ),
                    html.Div(
                        id="tabs-content-example",
                        className="canvas"),
                    dcc.Store(id="memory-stitch"),
                ], className="eight columns result",
            )],
            className="row twelve columns", )
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


@app.callback(Output("memory-stitch", "data"), [Input("go_button", "n_clicks")])
def update_store(click):
    return click


@app.callback(
    Output("tabs-content-example", "children"), [Input("crawl-tabs", "value")]
)
def fill_tab(tab):
    if tab == "tab-two":
        return [
            html.Div(
                [html.Div([
                    html.Br(),
                    html.Button('Calculate routes', id='go_button', className="button_submit"),
                    html.Div(id='controls-container', children=[
                        html.Img(
                            src=app.get_asset_url("giphy_walk.gif"),
                            id="walk-image",
                            style={
                                "height": "300px",
                                "width": "auto",
                                "margin-bottom": "0px",
                                "margin-top": "0px",
                            }, className="plotly-logo"
                        ),
                         html.Div(
                             [dcc.Graph(id="clustering_graph")],
                             className="pretty_container seven columns",
                         ),
                    ]),
                ]),
                    html.Br(),
                    html.Br(),
                    html.Div([
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        dcc.Graph(id="histogram")])],
                className="row twelve columns")]
    elif tab == "tab-three":
        return [html.Div(
            [html.Div([
                html.Br(),
                html.Button('Show route', id='details_button', className="button_submit"),
            ]),
                html.Div(
                    [html.Div(html.H3(id='combinations'), className='pretty_container six columns'),
                     html.Div(
                         html.H3(id='avg_rating'), className='pretty_container six columns')]
                    , className='row twelve columns'),
                html.Div(
                    [html.Div(html.H3(id='total_walking_time_act'), className='pretty_container six columns'),
                     html.Div(
                         html.H3(id='total_waiting_time_act'), className='pretty_container six columns')]
                    , className='row twelve columns')
            ],
            id="info-container",
            className="row container-display",
        ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="satellite_graph")],
                        className="pretty_container seven columns",
                    ),
                    # html.Div(
                    #    [dcc.Graph(id="individual_graph")],
                    #    className="pretty_container five columns",
                    # ),
                ],
                className="row eight columns",
            )]

    return [

        html.Label(
            "Welcome to the bar crawl simulator. Please select your desired settings on the left and apply the filters."),
        html.Img(
            src=app.get_asset_url("giphy (2).gif"),
            id="mit-image",
            style={
                "height": "400px",
                "width": "auto",
                "margin-bottom": "25px",
            }, className="plotly-logo"
        )]


# Helper functions
def human_format(num):
    magnitude = 1  # int(math.log(num, 1000))
    mantissa = str(int(num / (1000 ** magnitude)))
    return mantissa + ["", "K", "M", "G", "T", "P"][magnitude]


# Selectors -> main graph
@app.callback(
    Output("satellite_graph", "figure"),
    [Input("walking_time", "value"), Input("details_button", "n_clicks"), Input("crawl-tabs", "value")]
)
def make_main_figure(walking_time, go_button, tab):
    traces = []
    bar_num = 0
    walking_time = float(walking_time)
    solutions = pickle.load(open(DATA_PATH.joinpath("solutions.pkl"), "rb"))
    solution = [x for x in solutions if abs(x.max_walking_time - walking_time) < 1][0]
    with open('data/start_coordinates', 'rb') as handle:
        start_coordinates = pickle.load(handle)

    trace = dict(
        type="scattermapbox",
        lon=[start_coordinates["lng"]],
        lat=[start_coordinates["lat"]],
        text='Starting point',
        customdata='',
        name="Starting position",
        marker=dict(size=12, opacity=0.6),
    )
    traces.append(trace)

    for bar in solution.bars:
        bar_num = bar_num + 1
        trace = dict(
            type="scattermapbox",
            lon=[bar.longitude],
            lat=[bar.latitude],
            text=bar.name,
            customdata=bar.rating,
            name="{}. {} ".format(bar_num, bar.name),
            marker=dict(size=12, opacity=0.6),
        )
        traces.append(trace)

    avg_longitude = sum([bar.longitude for bar in solution.bars]) / bar_num
    avg_latitude = sum([bar.latitude for bar in solution.bars]) / bar_num
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
            center=dict(lon=avg_longitude, lat=avg_latitude),
            zoom=14,
        ),
    )

    figure = dict(data=traces, layout=layout)

    return figure


# Selectors -> main graph
@app.callback(
    Output("clustering_graph", "figure"), [Input("go_button", "n_clicks")]
)
def make_main_figure(n_clicks):
    traces = []
    df = pd.read_csv('data/processed_data.csv')
    coordinates = list(zip(df.latitude, df.longitude))
    df['cluster'] = get_clusters(coordinates, df['business_id'])
    df['cluster_name'] = 'Cluster # ' + df['cluster'].astype(str)
    for name, dff in df.groupby("cluster_name"):
        trace = dict(
            type="scattermapbox",
            lon=dff['longitude'],
            lat=dff['latitude'],
            text=dff['cluster_name'],
            customdata=dff['cluster_name'],
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
            center=dict(lon=-79.3871, lat=43.6626),
            zoom=11,
        ),
    )

    figure = dict(data=traces, layout=layout)

    return figure


@app.callback(Output("combinations", "children"),
              [Input("num_stops", "value"), Input("details_button", "n_clicks"), Input("crawl-tabs", "value")])
def total_combinations(num_stops, go_button, tab):
    with open('data/df_length.output', 'rb') as filehandle:
        length = int(filehandle.read())

    total_combinations = length
    for i in range(num_stops - 1):
        total_combinations = total_combinations * (length - i)
    return "Combinations considered: {:,}".format(total_combinations)


@app.callback(Output("avg_rating", "children"),
              [Input("walking_time", "value"), Input("details_button", "n_clicks"), Input("crawl-tabs", "value")])
def avg_rating(walking_time, go_button, tab):
    walking_time = float(walking_time)
    solutions = pickle.load(open(DATA_PATH.joinpath("solutions.pkl"), "rb"))

    solution = [x for x in solutions if abs(x.max_walking_time - walking_time) < 1][0]

    return "Average rating: {}".format(round(float(solution.avg_rating), 1))


@app.callback(Output("total_walking_time_act", "children"),
              [Input("walking_time", "value"), Input("details_button", "n_clicks"), Input("crawl-tabs", "value")])
def total_walk(walking_time, go_button, tab):
    walking_time = float(walking_time)
    solutions = pickle.load(open(DATA_PATH.joinpath("solutions.pkl"), "rb"))

    solution = [x for x in solutions if abs(x.max_walking_time - walking_time) < 1][0]

    return "Total walking time: {} mins".format(round(float(solution.total_walking_time) * 60, 1))


@app.callback(Output("total_waiting_time_act", "children"),
              [Input("walking_time", "value"), Input("details_button", "n_clicks"), Input("crawl-tabs", "value")])
def total_wait(walking_time, go_button, tab):
    walking_time = float(walking_time)
    solutions = pickle.load(open(DATA_PATH.joinpath("solutions.pkl"), "rb"))

    solution = [x for x in solutions if abs(x.max_walking_time - walking_time) < 1][0]

    return "Total waiting time: {} mins".format(round(float(solution.total_waiting_time) * 60, 1))


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


@app.callback(Output("crawl-tabs", "value"), [Input("apply_button", "n_clicks")], [State("address", "value")])
def change_focus(click, address):
    if click:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": config.KEY}
        r = requests.get(url, params=params)
        add = (r.json()['results'])
        try:
          coordinate_dict = add[0]['geometry']['location']
          print("Start coordinates {} {}".format(coordinate_dict['lat'], coordinate_dict['lng']))
        except:
            coordinate_dict = None
        #    coordinate_dict = {'lat':43.6426, 'lng':-79.3871}

        with open('data/start_coordinates', 'wb') as handle:
            pickle.dump(coordinate_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return "tab-two"
    return "tab-one"


@app.callback(Output('controls-container', 'style'), [Input('go_button', 'n_clicks'),
                                                      Input('histogram', 'figure')])
def toggle_container(toggle_value, graph):
    if toggle_value is None:
        return {'display': 'none'}
    if len(graph) > 1:
        return {'display': 'none'}
    if toggle_value >= 1:
        return {'display': 'block'}
    return {'display': 'none'}


@app.callback(
    Output("histogram", "figure"),
    [
        Input("go_button", "n_clicks"),
        Input("histogram", "clickData")
    ],
    [
        State("max_walking_time", "value"),
        State("crawl_date", "date"),
        State("start_time", "value"),
        State("end_time", "value"),
        State("budget_range", "value"),
        State("min_review_ct", "value"),
        State("min_review", "value"),
        State('single_walking_time', "value"),
        State("num_stops", "value"),
        State("max_waiting_time", "value"),
        State("unsupervised", "value"),
        State("walking_time", "value")
    ],
)
def get_pareto(nclicks, clickdata, total_max_walking_time, crawl_date, start_time, end_time, budget_range,
               min_review_ct, min_review, single_walking_time, num_stops, max_waiting_time, unsupervised,
               selected_walking_time):

    if nclicks is None:
        return {}

    if total_max_walking_time != '' and clickdata is None:
        crawl_date = parser.parse(crawl_date)
        total_max_walking_time = float(total_max_walking_time) / 60.0
        start_time = int(start_time)
        if start_time < 5:
            start_time = start_time + 24
        end_time = int(end_time)
        if end_time < 5:
            end_time = end_time + 24
        budget_range = [int(i) for i in budget_range]
        min_review_ct = int(min_review_ct)
        min_review = float(min_review)
        single_walking_time = float(single_walking_time) / 60
        num_stops = int(num_stops)
        max_waiting_time = int(max_waiting_time) / 60

        with open('data/start_coordinates', 'rb') as handle:
            start_coordinates = pickle.load(handle)
        print(start_coordinates)
        if start_coordinates is not None:
            start_coord = (start_coordinates['lat'], start_coordinates['lng'])
        else:
            start_coord = None
        solutions = crawl_model(min_review_ct, min_review, crawl_date, budget_range, start_time, end_time, num_stops,
                                total_max_walking_time, single_walking_time, max_waiting_time,
                                'data/processed_data.csv', 'data/distances.csv', start_coord, unsupervised)

        with open('data/solutions.pkl', 'wb') as handle:
            pickle.dump(solutions, handle, protocol=pickle.HIGHEST_PROTOCOL)
        xVal = []
        yVal = []
        for solution in solutions:
            print(solution.max_walking_time)
            xVal.append(solution.max_walking_time)
            yVal.append(round(solution.avg_rating, 1))
        xVal = np.array(xVal)
        yVal = np.array(yVal)
        np.savetxt('data/xVal.out', xVal)
        np.savetxt('data/yVal.out', yVal)
        if len(xVal) == 0:
            return {}
        colors = list(Color("blue").range_to(Color("green"), len(xVal)))
        walking_distance = float(total_max_walking_time)
        colors = [(255 * c.rgb[0], 255 * c.rgb[1], 255 * c.rgb[2], 0.5) for c in colors]
    else:
        xVal = np.loadtxt('data/xVal.out')
        yVal = np.loadtxt('data/yVal.out')
        colors = list(Color("blue").range_to(Color("green"), len(xVal)))
        colors = [(255 * c.rgb[0], 255 * c.rgb[1], 255 * c.rgb[2], 0.2) for c in colors]

    if selected_walking_time != '' and clickdata is not None and float(selected_walking_time) in xVal:
        walking_distance = float(selected_walking_time)

        c_selected = colors[np.where(xVal == walking_distance)[0][0]]
        colors[np.where(xVal == walking_distance)[0][0]] = (c_selected[0], c_selected[1], c_selected[2], 1.0)

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
        title="Select desired walking time / rating combination",
        font=dict(color="black"),
        xaxis=dict(
            title='Total time spent walking between bars (minutes)',
            range=[min(xVal), max(xVal)],
            showgrid=False,
            nticks=len(xVal),
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
