import os
import tempfile
import pandas as pd
from loguru import logger

REQUIRED_COLUMNS = ['sku', 'name', 'category', 'price', 'stock_qty', 'status']

def read_file(file):
    suffix = os.path.splitext(file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(file.read())
        tmp_file.flush()
        tmp_file_path = tmp_file.name

    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(tmp_file_path)
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(tmp_file_path)
        else:
            raise ValueError("Invalid file type. Only CSV or Excel files allowed.")
    finally:
        os.remove(tmp_file_path)

    return df


def validate_dataframe(df, file_name):
    errors = []

    if df.empty:
        errors.append("File is empty")
        return df, errors

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing columns: {', '.join(missing_columns)}")
        return df, errors

    for col in ['sku', 'name', 'category', 'status']:
        df[col] = df[col].astype(str).str.strip()

    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['stock_qty'] = pd.to_numeric(df['stock_qty'], errors='coerce')

    empty_skus = df['sku'].isnull() | (df['sku'] == '')
    if empty_skus.any():
        rows = df[empty_skus].index.tolist()
        errors.append(f"Empty SKUs found at rows: {rows}")
        df = df[~empty_skus]

    dup_in_file = df[df.duplicated(subset='sku', keep=False)]
    if not dup_in_file.empty:
        logger.info(f"{file_name}: Duplicate SKUs in file removed: {dup_in_file['sku'].tolist()}")
        errors.append(f"Duplicate SKUs removed in file: {dup_in_file['sku'].tolist()}")
        df = df.drop_duplicates(subset='sku', keep='last')

    return df, errors
