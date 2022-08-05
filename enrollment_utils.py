import pandas as pd
import numpy as np
from tqdm import tqdm
import datetime
from utils import create_translation_dic, get_uc_engineering_id

def get_enrollment_df(adm_year, translation_mapper, uc_eng_only=True):
    relevant_keys=['Career code (university-degree)', 'Masked ID for student','Year of academic process for admission']
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
    if uc_eng_only:
        df = df[df['Career code (university-degree)'] == get_uc_engineering_id(adm_year, sheet="enrollment")]

    #Only look at students with admission year equal to adm_year
    df = df[df['Year of academic process for admission']==adm_year]
    df = df[relevant_keys]
    df.reset_index(inplace=True, drop=True)
    all_df.append(df)
        
    main_df = pd.concat(all_df, ignore_index=True)
    return main_df

def get_enrolled_ids_year(adm_year, uc_eng_only=True):
    enrollment_mapper = create_translation_dic("Enrollment")
    df = get_enrollment_df(adm_year, enrollment_mapper, uc_eng_only)
    return set(df["Masked ID for student"])