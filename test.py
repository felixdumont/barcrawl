from datetime import datetime
from models.models import crawl_model
from preprocessing.business_processing import generate_full_csv


percentiles = [0.5,0.6,0.7,0.8,0.9,1.0]
wait_time_distr = [0,5,10,15,20,30]

#df = generate_full_csv('data/business.json', 'Toronto', 'data/checkin.json',
#                       'data/processed_data.csv', percentiles, wait_time_distr)

min_review_ct = 0
min_rating = 0
date = datetime(2019,8,9)
budget_range = [1, 2, 3, 4]
start_time = 17
end_time = 22
bar_num = 6
total_max_walking_time = 1.15
max_walking_each = 0.25
max_total_wait = 1
csv = "data/processed_data.csv"
distance_csv = "data/distances.csv"
solution = crawl_model(min_review_ct, min_rating, date, budget_range, start_time, end_time, bar_num,
                                 total_max_walking_time, max_walking_each, max_total_wait, csv, distance_csv)