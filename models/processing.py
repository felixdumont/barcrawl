# On the spot filtering. Different from the one-time preprocessing
from datetime import datetime
import pandas as pd
from preprocessing.business_utils import calculate_distance

def load_dataset(csv):
    """
    Load dataset from the preprocessed CSV
    :return:
    """
    df = pd.read_csv(csv)
    return df


def get_day_of_week(date):
    day_of_week = date.strftime('%A')
    return day_of_week


def filter_dataset(df, min_review_ct, min_rating, date, budget_range):
    #:param df, pre-processed data frame loaded from "load_dataset" function
    #:param min_review_ct:"
    #:param min_rating:"
    #:param date, loaded from "get_day_of_week" function

    day_of_week = str(get_day_of_week(date))

    #:list budget_range, list of budget ranges
    df = df[df['RestaurantsPriceRange2'].isin(
        budget_range)]  # filter for budget range, need to make sure input is a list with the right format
    df = df[(df['review_count'] >= min_review_ct) & (
            df['stars'] >= min_rating)]  # filter out bars without min review count or min rating

    # change open and close column to only be related to the day inputted by the user
    df['open'] = df[day_of_week + " open"]
    df['close'] = df[day_of_week + " close"]
    columns_to_drop = ['Monday open', 'Monday close', 'Tuesday open', 'Tuesday close',
                       'Wednesday open', 'Wednesday close', 'Thursday open', 'Thursday close', 'Friday open',
                       'Friday close',
                       'Saturday open', 'Saturday close', 'Sunday open', 'Sunday close']
    df = df.drop(columns=columns_to_drop)
    df = df.dropna(subset=['open', 'close'])
    return df


def dima_filtered(df, dima_df):
    keep_columns = dima_df.columns

    filtered = pd.merge(dima_df, df, how="inner", on=["business_id"])
    filtered = filtered[keep_columns]

    keep_columns = filtered.columns
    filtered = filtered.transpose()

    filtered = filtered.rename(columns=filtered.iloc[0])

    filtered = filtered.drop('business_id')
    filtered = filtered.reset_index()
    filtered = filtered.rename(columns={'index': 'business_id'})
    keep_columns = filtered.columns[1:]
    filtered = pd.merge(filtered, df, how="inner", on=["business_id"])
    filtered = filtered[keep_columns]

    dima = filtered.values.tolist()
    return dima


def closest_bar(df, start_coord):
    df_cp = df.copy()

    df_cp['dist_from_start'] = df_cp.apply(lambda x: calculate_distance((x['latitude'], x['longitude']), start_coord),
                                           axis=1)

    business_id = df_cp.loc[(df_cp.dist_from_start == df_cp.dist_from_start.min()), 'business_id'].values[0]

    return business_id