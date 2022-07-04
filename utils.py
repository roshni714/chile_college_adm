import pandas as pd
import pandas as pd
import numpy as np
from tqdm import tqdm
import datetime

def create_translation_dic(sheet_name):
    codebook_df = pd.read_excel("data/admissions/codebook_PSU.xlsx", sheet_name)
    temp_df = codebook_df[codebook_df['Variable'].notna()]
    spanish_key = temp_df["Variable"]
    english_key = temp_df['Description (English)']
    dic = dict(zip(spanish_key, english_key))
    return dic

def get_graduation_df(adm_year, num_sem, grad_mapper):
    relevant_keys=['Student identifier',
                   'Unique code for program',
                   'Year of admission as a freshman',
                   'Year of admission to the program',
                   'Semester of admission as a freshman',
                   'Name of the title conferred to the student',
                   'Date of the title (YYYYMMDD)',
                   'Total theoretical duration of the degree (in semesters)']
    
    all_df = []
    for i in tqdm(range(2007, min(adm_year + 8, 2021))):
        # Read in data
        df = pd.read_csv("data/graduation/Titulados-de-Educacion-Superior-{}/Titulados_Educacion_Superior_{}.csv".format(i,i), sep=";",
                        dtype={"MRUN": 'str' , "EDAD_ALU":'str', 'cod_carrera': 'str', 'version': 'str', 'cod_sede':'str', 
                               'dur_estudio_carr':'str', 'dur_proceso_tit':'str', 'dur_total_carr':'str' })
        # Replace empty strings with NaN
        df = df.replace(r'\s+',np.nan,regex=True).replace('',np.nan)
        
        # Translate columns
        df.columns = map(str.upper, df.columns)
        df = df.rename(columns=grad_mapper)
        
        #Only look at students with admission year equal to adm_year
        df = df[df['Year of admission as a freshman']==adm_year]
        if num_sem != None:
            df = df[df['Total theoretical duration of the degree (in semesters)']=="{}".format(num_sem)]
        
        # Drop rows that have NaN in important columns
        df = df[df['Year of admission as a freshman'].notna()]
        df = df[df['Semester of admission as a freshman'].notna()]
        df = df[df['Date of the title (YYYYMMDD)'].notna()]
        df = df[df['Total theoretical duration of the degree (in semesters)'].notna()]
        
        
        df = df[relevant_keys]
        df.reset_index(inplace=True, drop=True)
        all_df.append(df)
        
    main_df = pd.concat(all_df, ignore_index=True)
    return main_df


def get_enrollment_df(adm_year, translation_mapper):
    relevant_keys=['Masked ID for student','Year of academic process for admission']
    all_df = []
    # Read in data
    df = pd.read_csv("data/admissions/D_PSU_Matrícula/D_MATRICULA_PSU_{}_PRIV_MRUN.csv".format(adm_year), sep=";", encoding='latin-1')
    # Replace empty strings with NaN
    df = df.replace(r'\s+',np.nan,regex=True).replace('',np.nan)

    # Translate columns
    df.columns = map(str.upper, df.columns)
    df = df.rename(columns={'AÑO_PROCESO': 'ANYO_PROCESO', 
                            'CODIGO_CARRERA': 'CÓDIGO_CARRERA', 
                            'SEDE_CARRERA': 'SEDE', 
                            'LUGAR':'LUGAR_EN_LA_LISTA',
                            'POND_AÑO_ACAD':'POND_ANYO_ACAD',
                            'AÃO_PROCESO':'ANYO_PROCESO',
                            'POND_AÃO_ACAD': 'POND_ANYO_ACAD',
                            'Ï»¿TIPO_IDENTIFICACION': "TIPO_IDENTIFICACION"
                           })
    df = df.rename(columns=translation_mapper)

    #Only look at students with admission year equal to adm_year
    df = df[df['Year of academic process for admission']==adm_year]
    df = df[relevant_keys]
    df.reset_index(inplace=True, drop=True)
    all_df.append(df)
        
    main_df = pd.concat(all_df, ignore_index=True)
    return main_df

def get_socioeconomic_df(adm_year, threshold, translation_mapper):
    relevant_keys=['Masked ID for student', 'Year of academic process for admission', 'Family income']
    all_df = []
    # Read in data
    df = pd.read_csv("data/admissions/B_PSU_Socioeconomico/B_SOCIOECONOMICO_DOMICILIO_PSU_{}_PRIV_MRUN.csv".format(adm_year), sep=";", encoding='latin-1')
    # Replace empty strings with NaN
    df = df.replace(r'\s+',np.nan,regex=True).replace('',np.nan)

    # Translate columns
    df.columns = map(str.upper, df.columns)
    df = df.rename(columns={"TIPO_IDENTIFICACION":"TIPO_IDENTIFICACIÓN",
                            'AÑO_PROCESO': 'ANYO_PROCESO',
                            'CUANTOS_TRABAJAN_DEL_GRUPO_FAMILIAR':'CUANTOS_TRABAJAN_DEL_GRUPO_FAM',
                            'CUANTOS_ESTUDIAN_GRUPO_FAMILIAR_SUPERIOR': "PERSONAS_ESTUDIAN_SUP"})
    df = df.rename(columns=translation_mapper)

    #Only look at students with admission year equal to adm_year
    df = df[df['Year of academic process for admission']==adm_year]
    df = df[(df['Family income'] <= threshold) & (df['Family income'] > 0)]
    df = df[relevant_keys]
    df.reset_index(inplace=True, drop=True)
    all_df.append(df)
        
    main_df = pd.concat(all_df, ignore_index=True)
    return main_df

def get_enrolled_ids_year(adm_year):
    enrollment_mapper = create_translation_dic("Enrollment")
    df = get_enrollment_df(adm_year, enrollment_mapper)
    return set(df["Masked ID for student"])

def get_graduated_on_time_ids_year(adm_year):
    grad_mapper = create_translation_dic("Graduation")
    grad_df = get_graduation_df(adm_year, num_sem, grad_mapper)
    
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
    return set(on_time_grad_df["Student identifier"])


def get_low_socio_ids_year(adm_year, threshold):
    socio_mapper = create_translation_dic("Socioeconomic")
    df = get_socioeconomic_df(adm_year, threshold, socio_mapper)
    return set(df["Masked ID for student"])
    


    
