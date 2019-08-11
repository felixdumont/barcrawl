# On the spot filtering. Different from the one-time preprocessing
import pandas as pd


def load_dataset(data_input):
    """
    Load dataset from the preprocessed CSV
    :return:
    """
    df = pd.read_csv(data_input)
    return df


def get_day_of_week(date):
    pass


def filter_dataset(df, min_review_ct, min_review, date, budget_range, city):
    pass
