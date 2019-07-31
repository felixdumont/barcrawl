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
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
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
                    [
                        html.P(
                            "Filter by date (or select range in histogram):",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="hour_slider",
                            min=1960,
                            max=2017,
                            value=[1990, 2010],
                            className="dcc_control",
                        ),
                        html.P("Filter by budget range:", className="control_label"),
                        dcc.Dropdown(
                            id="well_statuses",
                            options=price_range_options,
                            multi=True,
                            value=[],
                            className="dcc_control",
                        ),
                        dcc.Checklist(
                            id="lock_selector",
                            options=[{"label": "Lock camera", "value": "locked"}],
                            className="dcc_control",
                        ),
                        html.P("Filter by neighborhood:", className="control_label"),
                        dcc.RadioItems(
                            id="well_type_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "Productive only ", "value": "productive"},
                                {"label": "Customize ", "value": "custom"},
                            ],
                            value="productive",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="well_types",
                            options=well_type_options,
                            multi=True,
                            value=list(NEIGHBORHOODS.keys()),
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
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
                                    [html.H6(id="well_text"), html.P("Total walking distance")],
                                    id="wells",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="gasText"), html.P("Combinations considered")],
                                    id="gas",
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
                        html.Div(dcc.Input(
                            id="walking_distance",
                            type='text',
                            placeholder='Max total walking distance'
                        )),

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
                    [dcc.Graph(id="main_graph")],
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

    magnitude = 1 #int(math.log(num, 1000))
    mantissa = str(int(num / (1000 ** magnitude)))
    return mantissa + ["", "K", "M", "G", "T", "P"][magnitude]


def filter_dataframe(df, well_statuses, well_types, hour_slider):
    dff = df[
        df["Well_Status"].isin(well_statuses)
        & df["Well_Type"].isin(well_types)
        & (df["Date_Well_Completed"] > dt.datetime(hour_slider[0], 1, 1))
        & (df["Date_Well_Completed"] < dt.datetime(hour_slider[1], 1, 1))
    ]
    return dff


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

"""
# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("count_graph", "figure")],
)
"""

@app.callback(
    Output("aggregate_data", "data"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("hour_slider", "value"),
    ],
)
def update_production_text(well_statuses, well_types, hour_slider):

    dff = filter_dataframe(df, well_statuses, well_types, hour_slider)
    selected = dff["API_WellNo"].values
    index, gas, oil, water = produce_aggregate(selected, hour_slider)
    return [human_format(sum(gas)), human_format(sum(oil)), human_format(sum(water))]


# Radio -> multi
@app.callback(Output("well_types", "value"), [Input("well_type_selector", "value")])
def display_type(selector):
    if selector == "all":
        return list(NEIGHBORHOODS.keys())
    elif selector == "productive":
        return ["GD", "GE", "GW", "IG", "IW", "OD", "OE", "OW"]
    return []

"""
# Slider -> count graph
@app.callback(Output("hour_slider", "value"), [Input("count_graph", "selectedData")])
def update_hour_slider(count_graph_selected):

    if count_graph_selected is None:
        return [1990, 2010]

    nums = [int(point["pointNumber"]) for point in count_graph_selected["points"]]
    return [min(nums) + 1960, max(nums) + 1961]
"""

# Selectors -> well text
@app.callback(
    Output("well_text", "children"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("hour_slider", "value"),
    ],
)
def update_well_text(well_statuses, well_types, hour_slider):

    dff = filter_dataframe(df, well_statuses, well_types, hour_slider)
    return dff.shape[0]


@app.callback(
    [
        Output("gasText", "children"),
        Output("oilText", "children"),
        Output("waterText", "children"),
    ],
    [Input("aggregate_data", "data")],
)
def update_text(data):
    return data[0] + "", data[1] + "", data[2] + ""


# Selectors -> main graph
@app.callback(
    Output("main_graph", "figure"),
    [
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("hour_slider", "value"),
    ],
    [State("lock_selector", "value"), State("main_graph", "relayoutData")],
)
def make_main_figure(
    well_statuses, well_types, hour_slider, selector, main_graph_layout
):

    #dff = filter_dataframe(df, well_statuses, well_types, hour_slider)
    dff = df
    traces = []
    for well_type, dfff in dff.groupby("Well_Type"):
        trace = dict(
            type="scattermapbox",
            lon=dfff["Surface_Longitude"],
            lat=dfff["Surface_latitude"],
            text=dfff["Well_Name"],
            customdata=dfff["API_WellNo"],
            name=NEIGHBORHOODS[well_type],
            marker=dict(size=4, opacity=0.6),
        )
        traces.append(trace)

    figure = dict(data=traces, layout=layout)
    return figure


# Main graph -> individual graph
@app.callback(Output("individual_graph", "figure"), [Input("main_graph", "hoverData")])
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
    Output("walking_distance", "value"),
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
        Input("well_statuses", "value"),
        Input("well_types", "value"),
        Input("hour_slider", "value"),
        Input("walking_distance", "value"),
        Input("main_graph", "hoverData"),
    ],
)
def make_aggregate_figure(well_statuses, well_types, hour_slider, walking_distance, main_graph_hover):

    xVal = np.array([30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95])
    yVal = np.array([2.5, 3.2, 3.5, 3.8, 4.0, 4.2, 4.4, 4.6, 4.7, 4.8, 4.8, 4.8, 4.8, 4.8])

    colors = list(Color("blue").range_to(Color("green"), len(xVal)))

    if walking_distance != '':
        walking_distance = float(walking_distance)
        colors = [(255*c.rgb[0], 255*c.rgb[1], 255*c.rgb[2], 0.2) for c in colors]
    else:
        colors = [(255*c.rgb[0], 255*c.rgb[1], 255*c.rgb[2], 0.5) for c in colors]
    if walking_distance in xVal:
        c_selected = colors[np.where(xVal == walking_distance)[0][0]]
        colors[np.where(xVal == walking_distance)[0][0]] = (c_selected[0], c_selected[1], c_selected[2], 0.5)

    colors = ['rgba({},{},{},{})'.format(round(a,0),round(b,0),round(c,0),d) for (a,b,c,d) in colors]
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
