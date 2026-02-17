# main.py
import pandas as pd
import re
import unicodedata
import plotly.express as px
from data_utils import rename_after_column, clean_columns, normalize_text

# =====================
# Configuración y Constantes
# =====================
google_sheets = {
    'gsheet_2010': 'https://docs.google.com/spreadsheets/d/1NZbfUM_kr3wkNpSdBUYPspYsPoZCmBKGwz7u7gTtZxE/edit?gid=1386807876#gid=1386807876',
    'gsheet_2011': 'https://docs.google.com/spreadsheets/d/1oxRoLXqxxiYEl259j_gmjqO46TX8W6jI6p4tNcnqMIM/edit?gid=1641093590#gid=1641093590',
    'gsheet_2012': 'https://docs.google.com/spreadsheets/d/1XPuP0fa1RAoPkH_hx3kP_T2SqeKb-TQLhg8VhuRgz5s/edit?gid=1616045159#gid=1616045159',
    'gsheet_2013': 'https://docs.google.com/spreadsheets/d/1sGVgb9WUs_oR54GPHLl1gaMap22u81OdvHFCbo25reg/edit?gid=540656633#gid=540656633',
    'gsheet_2014': 'https://docs.google.com/spreadsheets/d/11oOHfiXHvvA_XlO5iMojbnBviAwk6_Xw9uw9XVo4Fjc/edit?gid=1952631340#gid=1952631340',
    'gsheet_2015': 'https://docs.google.com/spreadsheets/d/1jr0JQ1SbsgKBj6BBR5eyh7bVh6HVHO737JB3FyPP-FE/edit?gid=1952631340#gid=1952631340',
    'gsheet_2016': 'https://docs.google.com/spreadsheets/d/1zdc1SdIoc74iJJ7Uk1hQ8ezTXdc0VHYUlWq1eKakSkI/edit?gid=1952631340#gid=1952631340',
    'gsheet_2017': 'https://docs.google.com/spreadsheets/d/1OY8YymIGJzEYTBVKwpkGE-vDsYz3rKSjNe1TUj3qt40/edit#gid=0',
    'gsheet_2018': 'https://docs.google.com/spreadsheets/d/1G4AHA5gTppfX7FCljkTNq3klBn20gA0ci0PReeNKcn4/edit?gid=0#gid=0',
    'gsheet_2019': 'https://docs.google.com/spreadsheets/d/1gECmI2yOJYcA9UDmfHTPZXv5v5kTcA-k37A5c8vBq7g/edit?gid=1952631340#gid=1952631340',
    'gsheet_2020': 'https://docs.google.com/spreadsheets/d/1s_g16Ttsm0S1_9oMH2xilgDMRNaJTALjjV-wAdR5xVc/edit#gid=1952631340',
    'gsheet_2021': 'https://docs.google.com/spreadsheets/d/1ul4zEar8EoiTggJevwpi5sfdaez1gsV3xWTy6u4VrO4/edit#gid=1952631340',
    'gsheet_2022': 'https://docs.google.com/spreadsheets/d/1LRLaBLwbV3up9N5e3-HlLKTlFAFy7-sj5pxbt5ml4hc/edit?gid=1952631340#gid=1952631340',
    'gsheet_2023': 'https://docs.google.com/spreadsheets/d/1W3ISt-tJlgZ7W_BJ5j22Ln5PBNKDOr7qa8X8Ipt7KMA/edit#gid=1952631340',
    'gsheet_2024': 'https://docs.google.com/spreadsheets/d/19sq-trJ3L809F_EChMvGwHYZEiC4B8aC/edit?gid=392110818#gid=392110818',
    'gsheet_2025': 'https://docs.google.com/spreadsheets/d/1w9zRApJRSq0o_YZxpCe3BcQzl5ocjMzM/edit?gid=392110818#gid=392110818',
    'gsheet_2026': 'https://docs.google.com/spreadsheets/d/1U_0siHk90P0989Q0OPhXFaJBVbztW_xN/edit?gid=392110818#gid=392110818'          
}

# Diccionario de mapeo de nombres de columnas para estandarización global
RENAME_MAP = {
    "categorias_red_chilena": "categoria_red_chilena",
    "registrado_sernameg": "registro_sernameg",
    "ulitma_fecha_modificacion": "ultima_fecha_modificacion",
    "informacion_actualizada_por_ultima_vez": "ultima_fecha_modificacion",
    "informe_del_poder_judicial": "informe_poder_judicial",
    "antecedentes_sobre_hecho": "antecedentes_hecho",
    'edad_victima': 'edad', 
    'nacionalidad_victima': 'nacionalidad', 
    'ocupacion_victima': 'ocupacion'
}

map_regiones = {
    # bio bio
    "biobio": "bio bio",

    # ohiggins
    "ohiggins": "o'higgins",
    "o'higgings": "o'higgins",

    # metropolitana
    "region metropolitana": "metropolitana",
    "metropolitano": "metropolitana",

    # araucania
    "la araucania": "araucania",

    # maule
    "el maule": "maule",

    #arica
    "arica": "arica y parinacota",

    #tarapaca
    "iquique": "tarapaca",

    #casos/especiales
    "metropolitana/tarapaca": "metropolitana"
}

# Diccionario para almacenar información extraída de cada sheet
extracted_sheet_info = {}
for name, url in google_sheets.items():
    spreadsheet_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)/', url)
    gid_match = re.search(r'#gid=(\d+)', url)
    spreadsheet_id = spreadsheet_id_match.group(1) if spreadsheet_id_match else 'N/A'
    gid = gid_match.group(1) if gid_match else '0' 
    extracted_sheet_info[name] = {
        'url': url,
        'spreadsheet_id': spreadsheet_id,
        'gid': gid
    }

# =====================
# Función principal de carga y limpieza de datos
# =====================
def load_google_sheets_data(sheet_info_dict, col_fin="ultima_fecha_modificacion"):
    """
    Descarga, limpia y concatena los datos de todas las hojas de Google Sheets.
    Retorna un DataFrame consolidado.
    """
    df_final = pd.DataFrame()
    for name, info in sheet_info_dict.items():
        csv_export_url = f"https://docs.google.com/spreadsheets/d/{info['spreadsheet_id']}/export?format=csv&gid={info['gid']}"
        try:
            if 'gsheet_2021' in name:
                df = pd.read_csv(csv_export_url, header=1, index_col=False)
            else:
                df = pd.read_csv(csv_export_url, header=2, index_col=False)
            # Limpieza de columnas
            df.columns = (
                df.columns
                .str.strip()
                .str.replace(r"^(?!.*_)[A-Za-zÁÉÍÓÚÑÜáéíóúñü]+[._\-]?\d+$", 
                     lambda m: re.sub(r"[._\-]?\d+$", "", m.group(0)),
                     regex=True)
            )
            df = df.loc[:, df.columns.str.strip() != ""]
            df = df.replace("-"," ")
            df = df.replace(r"^\s*$", pd.NA, regex=True)
            df = clean_columns(df)
            df = df.rename(columns={k: v for k, v in RENAME_MAP.items() if k in df.columns})
            df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
            df = df[pd.to_datetime(df['fecha'], errors='coerce').notna()]
            df = df.map(normalize_text)
            df = df.rename(columns={'femicidia': 'nombre_femicida', 'femicida': 'nombre_femicida' })
            df = rename_after_column(df, 'nombre_femicida', '_femicida')
            df = df.rename(columns={'edad': 'edad_victima', 'nacionalidad': 'nacionalidad_victima', 'ocupacion': 'ocupacion_victima'})
            df = df.loc[:, ~df.columns.str.contains("^unnamed")]
            df['region'] = df['region'].replace(map_regiones)
            df['categoria_red_chilena'] = df.assign(col_final=df["categoria_red_chilena"].fillna(df["tipificacion_red_chilena"])).drop(columns="tipificacion_red_chilena")

            if col_fin in df.columns:
                df = df.loc[:, :col_fin]
            df = df.dropna(how="all")
            # Solución de duplicados en index
            df = pd.DataFrame(df.to_numpy(), columns=list(df.columns))
            df_final = df_final.reset_index(drop=True)
            df = df.reset_index(drop=True)
            df_final = pd.concat([df_final, df], ignore_index=True, sort=False)
            print(f"  Successfully loaded {len(df)} rows from {name}.")
        except Exception as e:
            print(f"  Error loading data from {name}: {e}")
    return df_final

# =====================
# Ejecución principal
# =====================
if __name__ == "__main__":
    # Carga y limpieza de datos
    df_final = load_google_sheets_data(extracted_sheet_info)
    # Aquí puedes continuar con el análisis o visualización de df_final
    df_final.to_pickle("consolidated_data.pkl")