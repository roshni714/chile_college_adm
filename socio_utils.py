import pandas as pd
import numpy as np
from tqdm import tqdm
import datetime

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


def get_low_socio_ids_year(adm_year, threshold):
    socio_mapper = create_translation_dic("Socioeconomic")
    df = get_socioeconomic_df(adm_year, threshold, socio_mapper)
    return set(df["Masked ID for student"])