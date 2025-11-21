# data_load.py
import pandas as pd
import glob
import os

DATA_PATH = r"C:\Users\monke\Washington State University (email.wsu.edu)\Oje, Funso - locations"

def load_all_csvs(path=DATA_PATH):
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    dfs = {}
    for file in csv_files:
        name = os.path.basename(file).replace(".csv", "")
        df = pd.read_csv(file)
        dfs[name] = df

        # Print info about the file
        print(f"Loaded {name}:")
        print(f"  Rows: {df.shape[0]}, Columns: {df.shape[1]}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Date range: {df['datetime'].min()} → {df['datetime'].max()}")
        print("-" * 40)
    return dfs


def clean_gps(df, max_accuracy=50):
    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df = df[df["accuracy"] <= max_accuracy]
    df = df.dropna(subset=["datetime", "latitude", "longitude"])
    df = df.sort_values("datetime").reset_index(drop=True)
    return df
