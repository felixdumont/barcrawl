import pandas as pd


def read_json(file):
    return pd.read_json(file, lines=True)


def parse_attributes(attribute_field):
    pass


def clean_dtypes(df):
    df['categories'] = df['categories'].astype('str')
    # TODO: Add logic for other fields
    return df


def one_time_filter(df, city):
    """
    Removes all non-bars from the dataset and other locations we would never consider
    :param df:
    :return:
    """
    df_bars = df[(df['categories'].str.contains('Bars')
                  | df['categories'].str.contains('Nightlife')
                  | df['categories'].str.contains('Pubs'))
                 & (~df['categories'].str.contains('Sushi Bars')
                    & ~df['categories'].str.contains('Juice Bars'))]

    df_bars = openfilter(df_bars)
    df_bars = separate_attributes(df_bars)
    df_bars = cityfilter(df_bars, city)
    df_bars = hoursbyday(df_bars)
    df_bars = getcolumns(df_bars)

    # TODO: Add other cleaning
    return df_bars

def cityfilter(df, city):
    df = df[(df['city'].str.contains(city))]
    return df

def openfilter(df):
    df_open = df[(df['is_open']==1)]
    return df_open

def separate_attributes(df):
    attributes=df['attributes'].apply(pd.Series)
    df_att=pd.concat([df, attributes],axis=1).drop('attributes', axis=1)
    return df_att


def hoursbyday(df):
    #separate hours into days
    hours=df['hours'].apply(pd.Series)
    df_hrs=pd.concat([df, hours],axis=1).drop('hours', axis=1)

    #separate days into open/close times
    days=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in days:
        temp=df_hrs[day].str.split("-", n=1, expand=True)
        df_hrs[day+' open']=temp[0]
        df_hrs[day+' close']=temp[1]
    return df_hrs

def getcolumns(df):
    categories=['address','categories','city', 'latitude', 'longitude', 'name', 'RestaurantsPriceRange2','review_count','stars', 'Monday open', 'Monday close','Tuesday open', 'Tuesday close', 'Wednesday open', 'Wednesday close', 'Thursday open', 'Thursday close', 'Friday open', 'Friday close', 'Saturday open', 'Saturday close', 'Sunday open', 'Sunday close', 'Alcohol', 'WiFi']
    df_cols=df[categories]
    return df_cols

def generate_business_csv(json_file, file_dest, city):
    df = read_json(json_file)
    df = clean_dtypes(df)
    df = one_time_filter(df, city)
    df.to_csv(file_dest)
