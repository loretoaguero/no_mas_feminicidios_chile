import pandas as pd
import unicodedata
import re

def rename_after_column(df, columna, sufijo):
    """Renombra columnas duplicadas después de una columna específica agregando un sufijo."""
    cols = df.columns.tolist()
    if columna not in cols:
        return df
    idx = cols.index(columna)
    seen = set(cols[:idx+1])  
    new_cols = cols.copy()
    for i in range(idx+1, len(cols)):
        col = cols[i]
        if col in seen:
            new_cols[i] = f"{col}{sufijo}"
        else:
            seen.add(col)
    df.columns = new_cols
    return df

def clean_columns(df):
    """Normaliza y limpia los nombres de las columnas de un DataFrame."""
    def normalize(col):
        col = col.strip().replace(r"[._\-\s]?\d+$", "")
        col = unicodedata.normalize("NFKD", col)
        col = "".join(c for c in col if not unicodedata.combining(c))
        col = col.lower()
        col = re.sub(r"[^\w\s]", "", col)
        words = col.split()
        words = [w for w in words if (len(w) > 2) or w.isdigit()]
        return "_".join(words)
    df.columns = [normalize(c) for c in df.columns]
    return df

def normalize_text(x):
    """Normaliza y limpia texto unicode, lo pasa a minúsculas y elimina guiones."""
    if isinstance(x, str):
        return (
            unicodedata.normalize("NFKD", x)
            .encode("ascii", "ignore")
            .decode("utf-8")
            .lower()
            .strip()
            .replace("-", " ")
        )
    return x
