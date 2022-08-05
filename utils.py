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

def get_uc_engineering_id(year, sheet):
    if sheet=="enrollment":
        codes_df = pd.read_csv("data/UCEngineering_Codes_Enrollment.csv", encoding='latin-1')
        code_year_df = codes_df[codes_df["Year"]==year]
        return code_year_df["demre_code"].item()
    elif sheet=="graduation":
        codes_df = pd.read_excel("data/UCEngineering_Codes_Graduation.xlsx", sheet_name="{}".format(year))
        engineering_codes = list(codes_df["codigo_unico"])
        return engineering_codes