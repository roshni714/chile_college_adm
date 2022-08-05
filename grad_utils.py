import pandas as pd
import numpy as np
from tqdm import tqdm
import datetime

def get_graduation_df(adm_year, num_sem, translation_mapper, ids=None):
    relevant_keys=['Student identifier',
                   'Unique code for program',
                   'Year of admission as a freshman',
                   'Semester of admission as a freshman',
                   'Name of the degree conferred to the student',
                   'Date of the title (YYYYMMDD)',
                   'Total theoretical duration of the degree (in semesters)']
    
    all_df = []
    for i in tqdm(range(2007, 2021)):
        # Read in data
        df = pd.read_csv("data/graduation/Titulados-de-Educacion-Superior-{}/Titulados_Educacion_Superior_{}.csv".format(i,i), sep=";",
                        dtype={"MRUN": 'str' , "EDAD_ALU":'str', 'cod_carrera': 'str', 'version': 'str', 'cod_sede':'str', 
                               'dur_estudio_carr':'str', 'dur_proceso_tit':'str', 'dur_total_carr':'str' })
        
        # Translate columns
        df.columns = map(str.upper, df.columns)
        df = df.rename(columns=translation_mapper)
        
        #Only look at students with relevant ids
        if ids is not None:
            df = df[df['Unique code for program'].isin(ids)]
        
        #Only look at students with admission year equal to adm_year
        df = df[df['Year of admission as a freshman']==adm_year]
        if num_sem is not None:
            df = df[df['Total theoretical duration of the degree (in semesters)']=="{}".format(num_sem)]
        
        # Drop rows that have NaN in important columns
        df = df[df['Year of admission as a freshman'].notna()]
        df = df[df['Semester of admission as a freshman'].notna()]
        df = df[df['Date of the title (YYYYMMDD)'].notna()]
        df = df[df['Total theoretical duration of the degree (in semesters)'].notna()]
        df = df[df['Student identifier'].notna()]
        
        df = df[relevant_keys]
        df.reset_index(inplace=True, drop=True)
        
        
        # Replace empty strings with NaN
        df = df.replace(r'\s+',np.nan,regex=True).replace('',np.nan)
        df = df.fillna(value=np.nan)
        
        all_df.append(df)
        
    main_df = pd.concat(all_df, ignore_index=True)
    return main_df


def get_on_time_grad_ids_year(adm_year):
    grad_mapper = create_translation_dic("Graduation")
    grad_df = get_graduation_df(adm_year, None, grad_mapper)
    
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
    
    on_time_grad_df = grad_df[grad_df["On-Time Graduation"] == True]
    return set([int(i) for i in on_time_grad_df["Student identifier"]])