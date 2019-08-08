from models.processing import filter_dataset, load_dataset
from dataclasses import dataclass
from typing import List


@dataclass
class Bar:
    name: str
    latitude: str
    longitude: str
    rating: float


@dataclass
class Solution:
    bars: List[Bar]
    total_max_walking_time: float


def create_objective_function():
    pass


def get_optimal_route(df, start_time, end_time, bar_num, total_max_walking_time, max_walking_each):
    """

    :param df:
    :param start_time:
    :param end_time:
    :param bar_num:
    :param total_max_walking_time:
    :param max_walking_each:
    :return: A Solution class object representing the optimal solution
    """
    return


def get_pareto_routes(df, start_time, end_time, bar_num, total_max_walking_time, max_walking_each):
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
    interval_length = 5
    for max_time in range(0, int(total_max_walking_time), interval_length):
        solutions.append(get_optimal_route(df, start_time, end_time, bar_num, max_time, max_walking_each))
    pass


def crawl_model(date, start_time, end_time, budget, bar_num,  total_max_walking_time,  max_walking_each, min_review_ct,
                min_review, city):
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

    df = load_dataset()
    df = filter_dataset(df, min_review_ct, min_review, date, budget, city)
    pareto_list = get_pareto_routes(df, start_time, end_time, bar_num, total_max_walking_time, max_walking_each)

    return pareto_list