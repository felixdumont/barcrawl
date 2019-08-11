from models.processing import filter_dataset, load_dataset
from dataclasses import dataclass
from typing import List
from datetime import datetime
import pandas as pd
from gurobipy import *


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


def get_optimal_route(df, start_time, end_time, bar_num, total_max_walking_time, max_walking_each, max_total_wait, dima):
    """

    :param df:
    :param start_time:
    :param end_time:
    :param bar_num:
    :param total_max_walking_time:
    :param max_walking_each:
    :return: A Solution class object representing the optimal solution
    """

    # parameters
    bigm = 999999
    m = Model("opt_route")
    locations = df['name']
    bar_ids = df['business_id']
    ratings = df['stars']
    open_times = df['open']
    close_times = df['close']
    wait_times = df['wait_time'] / 60

    time_spent_each_bar = max(0.25, (end_time - start_time - total_max_walking_time - max_total_wait) / bar_num)

    y = []
    x = [[0 for j in range(len(locations))] for i in range(len(locations))]
    z = [[[0 for j in range(len(locations))] for i in range(len(locations))] for k in range(bar_num - 1)]
    #coordinates = list(zip(df.latitude, df.longitude))
    #dima = generate_distance_matrix(coordinates, df['business_id'], 'manhattan')

    # create decision variables
    for loc in bar_ids:
        y.append(m.addVar(vtype=GRB.BINARY, name="y_{}".format(loc)))

    for k in range(bar_num - 1):
        for i in range(len(locations)):
            for j in range(len(locations)):
                z[k][i][j] = m.addVar(vtype=GRB.BINARY, name="z_{},{},{}".format(k, locations[i], locations[j]))

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
    m.addConstr(start_time + zed * time_spent_each_bar + quicksum([z[w][i][j] * (dima[i][j] + wait_times[i])
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
    m.addConstr(start_time + zed * time_spent_each_bar + quicksum([z[w][i][j] * (dima[i][j] + wait_times[i])
                                                                   for i in range(len(locations))
                                                                   for j in range(len(locations))
                                                                   for w in range(bar_num - 1)]) <=
                quicksum([close_times[j] * quicksum([z[bar_num - 2][i][j] for i in range(len(locations))])
                          for j in range(len(locations))]))

    # Must exit last bar before close time
    m.addConstr(start_time + zed * time_spent_each_bar + quicksum([z[w][i][j] * (dima[i][j] + wait_times[i])
                                                                   for i in range(len(locations))
                                                                   for j in range(len(locations))
                                                                   for w in range(bar_num - 1)]) <= end_time)

    # Total wait time less than max allowed
    m.addConstr(quicksum([wait_times[i] * y[i] for i in range(len(locations))]) <= max_total_wait)
    m.setParam('TimeLimit', 30)
    m.setParam('MIPFocus', 1)
    m.optimize()
    return m, y, z


def get_pareto_routes(df, start_time, end_time, bar_num, total_max_walking_time, max_walking_each, max_total_wait, dima):
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
    for max_walking_time in range(bar_num*5, int(total_max_walking_time * 60), 5):
        bars = []
        model, y_var, z_var = get_optimal_route(df, start_time, end_time, bar_num, max_walking_time / 60,
                                               max_walking_each, max_total_wait, dima)

        locations = len(z_var[0])
        #if model is None:
        #    continue
        for k in range(len(z_var)):
            for i in range(locations):
                for j in range(locations):
                    if z_var[k][i][j].x != 0:
                        if k == 0:
                            bar_id = y_var[i].VarName[2:]
                        else:
                            bar_id = y_var[j].VarName[2:]

                        print(bar_id)
                        print(df.loc[lambda f: f['business_id'] == bar_id]['name'])
                        name = str(df.loc[lambda f: f['business_id'] == bar_id]['name'].values[0])
                        longitude = float(df.loc[lambda f: f['business_id'] == bar_id]['longitude'].values[0])
                        latitude = float(df.loc[lambda f: f['business_id'] == bar_id]['latitude'].values[0])
                        rating = str(df.loc[lambda f: f['business_id'] == bar_id]['stars'].values[0])
                        bars.append(Bar(bar_id, name, longitude, latitude, rating)) # This is ordered

        total_walk_time = sum([z_var[w][i][j] * dima[i][j]
                  for i in range(locations)
                  for j in range(locations)
                  for w in range(bar_num - 1)])
        avg_rating = model.objval/bar_num
        total_wait = sum([wait_times[i] * y_var[i] for i in range(locations)])

        best_solution = Solution(bars, total_walk_time, total_wait, avg_rating)
        solutions.append(best_solution)
    return solutions


def crawl_model(min_review_ct, min_rating, date, budget_range, start_time, end_time, bar_num, total_max_walking_time,
                max_walking_each, max_total_wait, csv, distance_csv):
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
    dima = pd.read_csv(distance_csv)
    dima = dima.values.tolist()
    # TODO - remove filter
    df = df[:100]

    #     Return one optimal solution
    #     optrout,z,y,x,dima = get_optimal_route(df, start_time, end_time, bar_num,
    #                                           total_max_walking_time, max_walking_each, max_total_wait)
    #   return optrout,z,y,x,dima
    pareto_df = get_pareto_routes(df, start_time, end_time, bar_num, total_max_walking_time, max_walking_each,
                                  max_total_wait, dima)

    return pareto_df
