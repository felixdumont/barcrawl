from models.processing import filter_dataset, load_dataset, dima_filtered, closest_bar
from dataclasses import dataclass
from typing import List
from datetime import datetime
import pandas as pd
from gurobipy import *
from models.clustering import get_clusters


@dataclass
class Bar:
    id: str
    name: str
    longitude: float
    latitude: float
    rating: float


@dataclass
class Solution:
    bars: List[Bar]
    total_walking_time: float
    total_waiting_time: float
    avg_rating: float # Optimal Gurobi obj. function
    max_walking_time: float


def set_seed(model_1_y, model_1_z):
    model_2_y = model_1_y
    model_2_z = model_1_z
    return model_2_y, model_2_z

def get_optimal_route(df, start_time, end_time, bar_num, total_max_walking_time, max_walking_each, max_total_wait, dima,
                      closest_bar_id, y_start, z_start):
    """
    :param df:
    :param start_time:
    :param end_time:
    :param bar_num:
    :param total_max_walking_time:
    :param max_walking_each:
    :return: A Solution class object representing the optimal solution
    """
    print("start Gurobi")
    # parameters
    bigm = 999999
    m = Model("opt_route")
    locations = df['name']
    bar_ids = df['business_id']
    ratings = df['stars']
    open_times = df['open']
    close_times = df['close']
    wait_times = df['wait_time'] / 60

    #bar_num = bar_num + 1

    time_spent_each_bar = max(0.25, (end_time - start_time - total_max_walking_time - max_total_wait) / bar_num)

    y = []
    #z = [[[0 for j in range(len(locations))] for i in range(len(locations))] for k in range(bar_num - 1)]

    # create decision variables
    for loc in bar_ids:
        y.append(m.addVar(vtype=GRB.BINARY, name="y_{}".format(loc)))

    #for k in range(bar_num - 1):
    #    for i in range(len(locations)):
    #        for j in range(len(locations)):
    #            z[k][i][j] = m.addVar(vtype=GRB.BINARY, name="z_{},{},{}".format(k, locations[i], locations[j]))
    z = [[[m.addVar(vtype=GRB.BINARY, name="z_{},{},{}".format(k, locations[i], locations[j]))
           for j in range(len(locations))] for i in range(len(locations))] for k in range(bar_num - 1)]

    ### objective function
    m.setObjective(quicksum([y[i] * ratings[i] for i in range(len(locations))]), GRB.MAXIMIZE)

    ### constraints
    # Number of locations visited
    m.addConstr(quicksum(y) == bar_num)

    # max total walk time
    m.addConstr(quicksum([z[w][i][j] * dima[i][j]
                           for i in range(len(locations))
                          for j in range(len(locations))
                          for w in range(bar_num - 1)]) <= total_max_walking_time)

    # max walk time between locations
    for k in range(bar_num - 1):
        m.addConstr(quicksum([z[k][i][j] * dima[i][j]
                              for i in range(len(locations))
                              for j in range(len(locations))]) <= max_walking_each)

    # rules about z
    # no movements between the same bar
    for k in range(bar_num - 1):
        for i in range(len(locations)):
            m.addConstr(z[k][i][i] == 0)

    # Add starting location
    if closest_bar_id is not None:
        for i in range(len(locations)):
            if bar_ids[i] == closest_bar_id:
                m.addConstr(y[i] == 1)
                m.addConstr(quicksum([z[0][i][j] for j in range(len(locations))]) == 1)

    # froms/tos upper bound
    for i in range(len(locations)):
        m.addConstr(quicksum([z[k][i][j] for k in range(bar_num - 1) for j in range(len(locations))])
                    + quicksum([z[k][j][i] for k in range(bar_num - 1) for j in range(len(locations))])
                    <= bigm * y[i])

    # froms/tos lower bound
    for i in range(len(locations)):
        m.addConstr(quicksum([z[k][i][j] for k in range(bar_num - 1) for j in range(len(locations))])
                    + quicksum([z[k][j][i] for k in range(bar_num - 1) for j in range(len(locations))])
                    >= y[i] / bigm)

    # can only have one 1 per movement matrix
    for k in range(bar_num - 1):
        m.addConstr(quicksum([z[k][i][j] for i in range(len(locations)) for j in range(len(locations))]) == 1)

    # make sure we don't vist the same bar twice
    # dimension1
    for i in range(len(locations)):
        m.addConstr(quicksum([z[k][i][j] for j in range(len(locations)) for k in range(bar_num - 1)]) <= 1)

    # dimension2
    for j in range(len(locations)):
        m.addConstr(quicksum([z[k][i][j] for i in range(len(locations)) for k in range(bar_num - 1)]) <= 1)

    # have to start from the bar you previously went to

    for k in range(1, bar_num - 1):
        for i in range(len(locations)):
            m.addConstr(quicksum([z[k - 1][j][i]
                                  for j in range(len(locations))]) == quicksum(
                [z[k][i][j] for j in range(len(locations))]))

    # open  time - only distance is considered for the time being
    for zed in range(bar_num - 1):
        m.addConstr(start_time + zed * time_spent_each_bar + quicksum([z[w][i][j] * (dima[i][j] + wait_times[i])
                                                                       for i in range(len(locations))
                                                                       for j in range(len(locations))
                                                                       for w in range(zed)]) >= quicksum(
            [open_times[i] * quicksum(z[zed][i])
             for i in range(len(locations))]))


    m.addConstr(start_time + (bar_num - 1) * time_spent_each_bar + quicksum([z[w][i][j] * (dima[i][j] + wait_times[i])
                                                                   for i in range(len(locations))
                                                                   for j in range(len(locations))
                                                                   for w in range(bar_num - 1)]) >=
                quicksum([open_times[j] * quicksum([z[bar_num - 2][i][j] for i in range(len(locations))])
                          for j in range(len(locations))]))
    # Close time constraint

    for zed in range(bar_num - 1):
        m.addConstr(start_time + zed * time_spent_each_bar + quicksum([z[w][i][j] * (dima[i][j] + wait_times[i])
                                                                       for i in range(len(locations))
                                                                       for j in range(len(locations))
                                                                       for w in range(zed)]) <= quicksum(
            [close_times[i] * quicksum(z[zed][i])
             for i in range(len(locations))]))

    m.addConstr(start_time + (bar_num - 1)  * time_spent_each_bar + quicksum([z[w][i][j] * (dima[i][j] + wait_times[i])
                                                                   for i in range(len(locations))
                                                                   for j in range(len(locations))
                                                                   for w in range(bar_num - 1)]) <=
                quicksum([close_times[j] * quicksum([z[bar_num - 2][i][j] for i in range(len(locations))])
                          for j in range(len(locations))]))

    # Must exit last bar before close time
    m.addConstr(start_time + (bar_num - 1) * time_spent_each_bar + quicksum([z[w][i][j] * (dima[i][j] + wait_times[i])
                                                                   for i in range(len(locations))
                                                                   for j in range(len(locations))
                                                                   for w in range(bar_num - 1)]) <= end_time)

    # Total wait time less than max allowed
    m.addConstr(quicksum([wait_times[i] * y[i] for i in range(len(locations))]) <= max_total_wait)
    #m.setParam('OutputFlag', 0)  # Also dual_subproblem.params.outputflag = 0
    m.setParam('TimeLimit', 30)
    m.setParam('MIPFocus', 1)

    for i in range(len(y_start)):
        try:
            y[i].start = y_start[i].x
        except:
            y[i].start = y_start[i]

    for i in range(len(y_start)):
        for j in range(len(y_start)):
            for k in range(len(z_start)):
                try:
                    z[k][i][j].start = z_start[k][i][j].x
                except:
                    z[k][i][j].start = z_start[k][i][j]

    #m.setParam('MIPGapAbs', 0.09*bar_num)
    print("Start optimizing")
    m.optimize()
    return m, y, z


def get_pareto_routes(df, start_time, end_time, bar_num, total_max_walking_time, max_walking_each, max_total_wait,
                      dima, closest_bar_id=None):
    """
    Returns total_max_walking_time / 5 suggested routes (e.g. one for 0-5 mins walk, one for 5-10 mins walk, etc.).
    Pareto routes contain
    :param df:
    :param start_time:
    :param end_time:
    :param bar_num:
    :param total_max_walking_time:
    :param max_walking_each:
    :return: A list of Solutions
    """
    solutions = []
    wait_times = df['wait_time'] / 60
    last_success = 0
    if int(total_max_walking_time)*60 > 40:
        step = 10
        min_time=20
    else:
        step = 5
        min_time=5
    for max_walking_time in range(min_time, int(total_max_walking_time * 60), step):
        bars = []
        print("Running Pareto for max walking time {}".format(max_walking_time))
        if max_walking_time == min_time or last_success == 0:
            y_start = [0 for i in range(len(df))]
            z_start = [[[0 for j in range(len(df))] for i in range(len(df))] for k in range(bar_num - 1)]
        else:
            y_start, z_start = set_seed(y_var, z_var)
        model, y_var, z_var = get_optimal_route(df, start_time, end_time, bar_num, max_walking_time / 60,
                                               max_walking_each, max_total_wait, dima, closest_bar_id, y_start, z_start)

        locations = len(z_var[0])
        if model.status in [3,4,5]: # If infeasible or unbounded
            continue
        try:
            obj_val = float(model.objval)
        except:
            continue
        if model.objval < 0 or model.objval > 5*bar_num:
            continue
        last_success = 1
        for k in range(len(z_var)):
            for i in range(locations):
                for j in range(locations):
                    if z_var[k][i][j].x != 0:
                        if k == 0:
                            bar_id = y_var[i].VarName[2:]
                            name = str(df.loc[lambda f: f['business_id'] == bar_id]['name'].values[0])
                            longitude = float(df.loc[lambda f: f['business_id'] == bar_id]['longitude'].values[0])
                            latitude = float(df.loc[lambda f: f['business_id'] == bar_id]['latitude'].values[0])
                            rating = str(df.loc[lambda f: f['business_id'] == bar_id]['stars'].values[0])
                            bars.append(Bar(bar_id, name, longitude, latitude, rating)) # This is ordered

                        bar_id = y_var[j].VarName[2:]
                        name = str(df.loc[lambda f: f['business_id'] == bar_id]['name'].values[0])
                        longitude = float(df.loc[lambda f: f['business_id'] == bar_id]['longitude'].values[0])
                        latitude = float(df.loc[lambda f: f['business_id'] == bar_id]['latitude'].values[0])
                        rating = str(df.loc[lambda f: f['business_id'] == bar_id]['stars'].values[0])
                        bars.append(Bar(bar_id, name, longitude, latitude, rating))  # This is ordered

        total_walk_time = sum([z_var[w][i][j].x * dima[i][j]
                  for i in range(locations)
                  for j in range(locations)
                  for w in range(bar_num - 1)])
        avg_rating = model.objval/bar_num
        total_wait = sum([wait_times[i] * y_var[i].x for i in range(locations)])

        best_solution = Solution(bars, total_walk_time, total_wait, avg_rating, max_walking_time)
        solutions.append(best_solution)

    return solutions


def crawl_model(min_review_ct, min_rating, date, budget_range, start_time, end_time, bar_num, total_max_walking_time,
                max_walking_each, max_total_wait, csv, distance_csv, start_coord, create_clusters):
    """
    :param date:
    :param start_time:
    :param end_time:
    :param budget:
    :param bar_num:
    :param total_max_walking_time:
    :param max_walking_each:
    :param min_review_ct:
    :param min_review:
    :param city:
    :return:
    """

    df = load_dataset(csv)
    df = filter_dataset(df, min_review_ct, min_rating, date, budget_range).reset_index()

    if create_clusters:
        coordinates = list(zip(df.latitude, df.longitude))
        df['cluster'] = get_clusters(coordinates, df['business_id'])
    else:
        df['cluster'] = 0

    length = str(df.shape[0])
    with open('data/df_length.output', 'w') as filehandle:
        filehandle.write(length)

    dima_df = pd.read_csv(distance_csv, header = 0)
    max_index = 10000

    closest_bar_id = None
    if start_coord is not None:
        closest_bar_id = closest_bar(df[:max_index], start_coord)
        closest_bar_cluster = df.loc[lambda f: f['business_id'] == closest_bar_id]['cluster'].min()

        print("Closest bar is {}".format(closest_bar_id))

    print("{} bars before filtering".format(df.shape[0]))
    if closest_bar_id is not None:
        bars_close_enough = list(dima_df.loc[lambda f: f[closest_bar_id] <= total_max_walking_time]['business_id'])

        df = df[(df['business_id'].isin(bars_close_enough)) & (df['cluster'] == closest_bar_cluster)
        ].reset_index()

    dima = dima_filtered(df, dima_df)
    print("{} bars after filtering".format(df.shape[0]))

    # TODO - remove filter
    df = df[:max_index]
    print("WALK {}".format(total_max_walking_time))
    pareto_df = get_pareto_routes(df, start_time, end_time, bar_num, total_max_walking_time, max_walking_each,
                                  max_total_wait, dima, closest_bar_id)

    return pareto_df