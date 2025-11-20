# main.py
import os
import pandas as pd
from data_load import load_all_csvs, clean_gps
from clustering import cluster_locations_per_month, compute_time_spent
from analysis import top_locations_monthly, movement_transitions, weekday_weekend_stats
from mapping import make_maps_for_user

CLUSTERED_DIR = "clustered_outputs"


def main(run_clustering: bool = True):
    print("\n=== Loading CSV Files ===\n")
    datasets = load_all_csvs()  # prints info while loading

    print("\n=== Cleaning Data ===\n")
    cleaned = {}
    for name, df in datasets.items():
        clean_df = clean_gps(df)
        clean_df["datetime"] = pd.to_datetime(clean_df["datetime"])
        cleaned[name] = clean_df
        print(f"{name}: {clean_df.shape[0]} rows remain after cleaning")

    os.makedirs(CLUSTERED_DIR, exist_ok=True)
    clustered = {}

    if run_clustering:
        print("\n=== Clustering Locations Per Month ===\n")
        for name, df in cleaned.items():
            cluster_df = cluster_locations_per_month(
                df, eps_meters=50, min_samples=5, n_jobs=-1
            )
            clustered[name] = cluster_df

            # save to CSV so we can reuse without reclustering
            out_path = os.path.join(CLUSTERED_DIR, f"{name}_clustered.csv")
            cluster_df.to_csv(out_path, index=False)

            unique_clusters = cluster_df["cluster"].unique()
            n_clusters = len(unique_clusters) - (1 if -1 in unique_clusters else 0)
            print(f"{name}: {n_clusters} clusters detected (saved to {out_path})")
    else:
        print("\n=== Loading PRE-COMPUTED Clustered Data ===\n")
        for name in cleaned.keys():
            path = os.path.join(CLUSTERED_DIR, f"{name}_clustered.csv")
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Expected clustered file not found for {name}: {path}. "
                    "Run with run_clustering=True at least once first."
                )
            df = pd.read_csv(path, parse_dates=["datetime"])
            clustered[name] = df
            print(f"{name}: loaded {df.shape[0]} rows from {path}")

    print("\n=== Top 5 Locations Per Month ===\n")
    for name, df in clustered.items():
        print(f"\n{name}:")
        top5 = top_locations_monthly(df, n=5)
        for month, dwell_df in top5.items():
            print(f"  Month: {month}")
            print(dwell_df[["cluster", "hours"]].to_string(index=False))

    print("\n=== Weekday vs Weekend Time Spent ===\n")
    for name, df in clustered.items():
        week, weekend = weekday_weekend_stats(df)
        print(f"\n{name}:")
        print("  Weekdays clusters (hours):")
        print(week[["cluster", "hours"]].to_string(index=False))
        print("  Weekends clusters (hours):")
        print(weekend[["cluster", "hours"]].to_string(index=False))

    print("\n=== Movement Transitions ===\n")
    for name, df in clustered.items():
        transitions = movement_transitions(df)
        print(f"{name}: {len(transitions)} transitions detected")
        print(transitions.head(5).to_string(index=False))

    print("\n=== Generating Maps ===\n")
    for name, df in clustered.items():
        print(f"Generating maps for {name}...")
        make_maps_for_user(name, df)


if __name__ == "__main__":
    # first run: set to True to compute + save clusters
    # later runs (for mapping/analysis only): change to False
    main(run_clustering=False)
