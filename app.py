# Import required libraries
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

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

app.config['suppress_callback_exceptions'] = True

price_range_options = [
    {"label": price_range, "value": price_range}
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
        zoom=15,
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
                                    html.Div([
                                        html.Label(
                                            "Select a date:"
                                        ),
                                    ], className="eight columns", hidden=True),
                                ], className="mobile_forms", hidden=True),
                                html.Div([
                                    html.Div([
                                        html.Label(
                                            "Select a date:"
                                        ),
                                        dcc.DatePickerSingle(
                                            id='crawl_date',
                                            min_date_allowed=dt.datetime.today(),
                                            #with_portal=True,
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
                                        id="well_statuses",
                                        options=price_range_options,
                                        multi=True,
                                        value=[],
                                        className="dcc_control",
                                    ), ], className="eight columns"),
                                html.Div([
                                    html.Label("Number of bars"),
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
                                        ))], className="eight columns"),
                                html.Div([
                                    html.Div([
                                        html.Label("Max total walking time"),
                                        html.Div(dcc.Input(
                                            id="max_walking_time",
                                            type='text',
                                            value=60,
                                            placeholder='Max total walking time'
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
                                            value=5,
                                            placeholder='Min number of reviews by bar'
                                        )), ], className="six columns"),
                                    html.Div([
                                        html.Label("Min bar review (from 0 to 5)"),
                                        html.Div(dcc.Input(
                                            id="min_review",
                                            type='text',
                                            value=3,
                                            placeholder='Min bar review'
                                        )), ], className="six columns"),
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
                ]),
                    html.Div([
                        dcc.Graph(id="histogram")])],
                className="row twelve columns")]
    elif tab == "tab-three":
        return [html.Div(
            [html.Div([
                html.Br(),
                html.Button('Show route', id='details_button', className="button_submit"),
            ]),
                html.Div(
                    [html.Div(html.H1(id='combinations'), className='pretty_container six columns'),
                     html.Div(
                         html.H1(id='avg_rating'), className='pretty_container six columns')]
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
                    #html.Div(
                    #    [dcc.Graph(id="individual_graph")],
                    #    className="pretty_container five columns",
                   # ),
                ],
                className="row eight columns",
            )]

    return [
        html.Label("Welcome to the bar crawl simulator. Please select your desired settings on the left and press GO."),
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
    [Input("walking_time", "value"), Input("details_button", "n_clicks")]
)
def make_main_figure(walking_time, go_button):
    # dff = filter_dataframe(df, well_statuses, well_types, hour_slider)
    df = pd.read_csv('business.csv')
    df_bars = df[(df['categories'].str.contains('Bars')
                  | df['categories'].str.contains('Nightlife')
                  | df['categories'].str.contains('Pubs'))
                 & (~df['categories'].str.contains('Sushi Bars')
                    & ~df['categories'].str.contains('Juice Bars'))]
    dff = df_bars.loc[lambda f: f['city'] == 'Toronto'][:10]
    dff['rounded_review'] = round(dff['stars'], 0)
    traces = []
    bar_num = 0
    for name, dfff in dff.groupby("name"):
        bar_num = bar_num + 1
        trace = dict(
            type="scattermapbox",
            lon=dfff["longitude"],
            lat=dfff["latitude"],
            text=dfff['name'],
            customdata=dfff["rounded_review"],
            name="{}. {} ".format(bar_num, name),
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


@app.callback(Output("combinations", "children"),
              [Input("details_button", "n_clicks")],
              [State("num_stops", "value")])
def filter_dataframe(go, num_stops):
    # TODO: Call model from here
    return "Combinations considered: {:,}".format(num_stops*1241245)


@app.callback(Output("avg_rating", "children"),
              [Input("details_button", "n_clicks")],
              [State("num_stops", "value")])
def avg_rating(go, num_stops):
    # TODO: Call model from here
    return "Average rating: {}".format(round(float(num_stops), 1))


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
    ],

)
def make_aggregate_figure(nclicks, clickdata, walking_distance):
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


@app.callback(Output("crawl-tabs", "value"), [Input("apply_button", "n_clicks")])
def change_focus(click):
    if click:
        return "tab-two"
    return "tab-one"

# Main
if __name__ == "__main__":
    app.run_server(debug=True)
