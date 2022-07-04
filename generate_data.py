import os
import pandas as pd
import numpy as np
from tqdm import tqdm
import datetime

os.mkdir("processed_data")
os.mkdir("processed_data/graduation/")
os.mkdir("processed_data/enrollment/")
os.mkdir("processed_data/socioeconomic/")

years = list(range(2007, 2016))

print("Processing graduation data...")
for year in tqdm(years):
    grad_mapper = create_translation_dic("Graduation")
    grad_df = get_graduation_df(year, None, grad_mapper)
    
    #Compute on-time graduation
    adm_sem = grad_df['Semester of admission as a freshman'].astype("int").to_numpy()
    adm_year = grad_df['Year of admission as a freshman'].astype("int").to_numpy()
    month_dic = {1:3, 2:7}
    adm_month = [*map(month_dic.get, adm_sem)]
    adm_dates = [datetime.date(year=adm_year[i], month=adm_month[i], day=1) for i in range(len(adm_year))]
    deg_date = grad_df['Date of the title (YYYYMMDD)'].astype("str")
    deg_dates = [datetime.date(year=int(x[:4]), month=int(x[4:6]), day=int(x[6:])) for x in deg_date ]
    durations = np.array([round((deg_dates[i] - adm_dates[i]).days/365, 1) for i in range(len(adm_dates))])
    length_degree = grad_df['Total theoretical duration of the degree (in semesters)'].astype("int").to_numpy()/2
    on_time_grad = (durations <= length_degree)
    grad_df["On-Time Graduation"] = on_time_grad
    grad_df.to_csv('processed_data/graduation/{}.csv'.format(year))


print("Processing enrollment data...")
for year in tqdm(years):
    enrollment_mapper = create_translation_dic("Enrollment")
    enroll_df = get_enrollment_df(adm_year, enrollment_mapper)
    enroll_df.to_csv('processed_data/enrollment/{}.csv'.format(year))


print("Processing socioeconomic data...")
for year in years:
    socio_mapper = create_translation_dic("Socioeconomic")
    socio_df = get_socioeconomic_df(adm_year, socio_mapper)
    socio_df.to_csv('processed_data/socioeconomic/{}.csv'.format(year))
