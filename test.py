from datetime import datetime
from models.models import crawl_model
from preprocessing.business_processing import generate_full_csv
from preprocessing.business_utils import calculate_distance, walking_time, generate_distance_matrix
from models.clustering import get_clusters
import pandas as pd
import time

percentiles = [0.5,0.6,0.7,0.8,0.9,1.0]
wait_time_distr = [0,5,10,15,20,30]

#df = generate_full_csv('data/business.json', 'Toronto', 'data/checkin.json',
#                       'data/processed_data.csv', percentiles, wait_time_distr)


start = time.time()

min_review_ct = 20
min_rating = 3.7
date = datetime(2019,8,9)
budget_range = [1, 2, 3, 4]
start_time = 17
end_time = 22
bar_num = 6
total_max_walking_time = 1
max_walking_each = 0.35
max_total_wait = 1.0
csv = "data/processed_data.csv"
distance_csv = "data/distances.csv"
start_coord = (43.6426, -79.3871)
solutions = crawl_model(min_review_ct, min_rating, date, budget_range, start_time, end_time, bar_num,
                                 total_max_walking_time, max_walking_each, max_total_wait, csv, distance_csv,
                        start_coord, True)

for solution in solutions:
    print("--- Walking time is {}".format(solution.total_walking_time))
    print("--- Waiting time is {}".format(solution.total_waiting_time))
    for bar in solution.bars:
        print(bar.name + "; " + bar.id)

print("--- %s seconds ---" % (time.time() - start))
"""
df = pd.read_csv('data/processed_data.csv')
coordinates = list(zip(df.latitude, df.longitude))
df['cluster'] = get_clusters(coordinates,  df['business_id'])


import plotly.express as px
#px.set_mapbox_access_token(open(".mapbox_token").read())
carshare = px.data.carshare()
fig = px.scatter_mapbox(df, lat="latitude", lon="longitude",     color="cluster",
                  color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
fig.show()
"""