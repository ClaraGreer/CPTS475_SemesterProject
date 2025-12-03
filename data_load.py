# data_load.py
import pandas as pd
import glob
import os

DATA_PATH = r"C:\Users\clara\Washington State University (email.wsu.edu)\Oje, Funso - locations"

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

def clean_gps(df, max_accuracy=50):

    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]
    original_rows = len(df)

    # Parse datetime
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    after_parse = len(df)

    # Filter by accuracy
    df = df[df["accuracy"] <= max_accuracy]
    after_accuracy = len(df)

    # Drop rows with missing required fields
    df = df.dropna(subset=["datetime", "latitude", "longitude"])
    after_dropna = len(df)

    # Sort by time
    df = df.sort_values("datetime").reset_index(drop=True)

    print(
        f"Clean GPS: {original_rows} -> {after_parse} (parsed datetime) -> "
        f"{after_accuracy} (accuracy <= {max_accuracy}) -> "
        f"{after_dropna} (after dropna)"
    )

    return df

