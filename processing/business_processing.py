import pandas as pd


def read_json(file):
    return pd.read_json(file, lines=True)


def parse_attributes(attribute_field):
    pass


def clean_dtypes(df):
    df['categories'] = df['categories'].astype('str')
    # TODO: Add logic for other fields
    return df


def filter_bars(df):
    df_bars = df[(df['categories'].str.contains('Bars')
                  | df['categories'].str.contains('Nightlife')
                  | df['categories'].str.contains('Pubs'))
                 & (~df['categories'].str.contains('Sushi Bars')
                    & ~df['categories'].str.contains('Juice Bars'))]

    # TODO: Add other cleaning
    return df_bars


def generate_business_csv(json_file, file_dest):
    df = read_json(json_file)
    df = clean_dtypes(df)
    df = filter_bars(df)
    df.to_csv(file_dest)
