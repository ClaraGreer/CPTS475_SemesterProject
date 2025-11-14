# main.py
import pandas as pd
from data_load import load_all_csvs, clean_gps
from clustering import cluster_locations_per_month, compute_time_spent
from analysis import top_locations_monthly, movement_transitions, weekday_weekend_stats


def main():
    print("\n=== Loading CSV Files ===\n")
    datasets = load_all_csvs()  # prints info while loading

    print("\n=== Cleaning Data ===\n")
    cleaned = {}
    for name, df in datasets.items():
        clean_df = clean_gps(df)
        clean_df['datetime'] = pd.to_datetime(clean_df['datetime']) 
        cleaned[name] = clean_df
        print(f"{name}: {clean_df.shape[0]} rows remain after cleaning")

    print("\n=== Clustering Locations Per Month ===\n")
    clustered = {}
    for name, df in cleaned.items():
        cluster_df = cluster_locations_per_month(df, eps_meters=50, min_samples=5, n_jobs=-1)
        clustered[name] = cluster_df
        n_clusters = len(cluster_df['cluster'].unique()) - (1 if -1 in cluster_df['cluster'].unique() else 0)
        print(f"{name}: {n_clusters} clusters detected")

    print("\n=== Top 5 Locations Per Month ===\n")
    for name, df in clustered.items():
        print(f"\n{name}:")
        top5 = top_locations_monthly(df, n=5)
        for month, dwell_df in top5.items():
            print(f"  Month: {month}")
            print(dwell_df[['cluster', 'hours']].to_string(index=False))

    print("\n=== Weekday vs Weekend Time Spent ===\n")
    for name, df in clustered.items():
        week, weekend = weekday_weekend_stats(df)
        print(f"\n{name}:")
        print(f"  Weekdays clusters (hours):")
        print(week[['cluster', 'hours']].to_string(index=False))
        print(f"  Weekends clusters (hours):")
        print(weekend[['cluster', 'hours']].to_string(index=False))

    print("\n=== Movement Transitions ===\n")
    for name, df in clustered.items():
        transitions = movement_transitions(df)
        print(f"{name}: {len(transitions)} transitions detected")
        print(transitions.head(5).to_string(index=False))  # show first 5 transitions

    print("\n=== Generating Maps ===\n")
    # generate maps wooOOoo

if __name__ == "__main__":
    main()
