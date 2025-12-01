# main.py
import os
import pandas as pd
from IPython.display import display
from data_load import load_all_csvs, clean_gps
from clustering import cluster_locations_per_month, compute_time_spent
from analysis import top_locations_monthly, movement_transitions, weekday_weekend_stats
from mapping import make_maps_for_user

CLUSTERED_DIR = "clustered_outputs"


def main(run_clustering: bool = False, run_mapping: bool = False):
    print("\n=== Loading CSV Files ===\n")
    datasets = load_all_csvs()  # prints info while loading


    print("\n=== Cleaning Data ===\n")
    cleaned = {}
    for name, df in datasets.items():
        clean_df = clean_gps(df)
        # make sure datetime is parsed (backup, though clean_gps should already do it)
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

            # >>> NEW: detailed clustering stats <<<
            total_points = len(cluster_df)
            noise_points = (cluster_df["cluster"] == -1).sum()
            non_noise_points = total_points - noise_points

            unique_clusters = cluster_df["cluster"].unique()
            n_clusters = len(unique_clusters) - (1 if -1 in unique_clusters else 0)

            print(
                f"{name}: {n_clusters} clusters detected "
                f"(total points={total_points}, non-noise={non_noise_points}, noise={noise_points}) "
                f"(saved to {out_path})"
            )
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
    top5_clusters = {}

    for name, df in clustered.items():
        print(f"\n{name}:")
        top5 = top_locations_monthly(df, n=5)
        top5_clusters[name] = {}
        for month, dwell_df in top5.items():
            print(f"  Month: {month}")
            print(dwell_df[['cluster', 'hours']].head(5).to_string(index=False))

            # Store clusters present for mapping
            top5_clusters[name][month] = dwell_df["cluster"].tolist()
         

    print("\n=== Weekday vs Weekend Time Spent (Top 5 Clusters) ===\n")
    for name, df in clustered.items():
        week, weekend = weekday_weekend_stats(df)

        # Exclude noise cluster -1
        week = week[week['cluster'] != -1].head(5)
        weekend = weekend[weekend['cluster'] != -1].head(5)

        print(f"\n{name}:")
        print("  Weekdays (hours spent in top clusters):")
        if not week.empty:
            print(week[['cluster', 'hours']].to_string(index=False))
        else:
            print("    No weekday clusters found.")

        print("  Weekends (hours spent in top clusters):")
        if not weekend.empty:
            print(weekend[['cluster', 'hours']].to_string(index=False))
        else:
            print("    No weekend clusters found.")


    print("\n=== Movement Transitions ===\n")
    for name, df in clustered.items():
        transitions = movement_transitions(df)
        print(f"{name}: {len(transitions)} transitions detected")
        print(transitions.head(5).to_string(index=False))


    if run_mapping:
        print("\n=== Generating Maps ===\n")
        # find the correlated top 5 in clustered to generate maps
        top5_dated = {}

        for name, df in clustered.items():
            newdf = df.copy()
            newdf["month"] = newdf["datetime"].dt.to_period("M")

            # remove -1 clusters completely
            newdf = newdf[newdf["cluster"] != -1]

            # only keep months that have top 5 clusters
            valid_months = [pd.Period(m) for m in top5_clusters[name].keys()]
            newdf = newdf[newdf["month"].isin(valid_months)]

            def get_top5(group):
                month_str = str(group.name)
                top_clusters = top5_clusters[name].get(month_str, [])
                return group[group["cluster"].isin(top_clusters)]

            newdf = newdf.groupby("month", group_keys=False).apply(get_top5)

            top5_dated[name] = newdf

        # Generate the top 5 location maps for each person
        for name, df in top5_dated.items():
            print(f"Generating maps for {name}...")
            make_maps_for_user(name, df)

    print("\n=== Summary for Presentation ===\n")
    for name, df in clustered.items():
        total_points = len(df)
        noise_points = (df["cluster"] == -1).sum()
        non_noise_points = total_points - noise_points
        n_clusters = df["cluster"].nunique() - (1 if -1 in df["cluster"].unique() else 0)

        # Get overall top 5 clusters across all months
        cluster_hours = compute_time_spent(df)
        cluster_hours = cluster_hours[cluster_hours['cluster'] != -1]
        top_overall = cluster_hours.head(5)['cluster'].tolist()

        print(
            f"{name}: {n_clusters} clusters, {non_noise_points}/{total_points} points non-noise, "
            f"Top overall clusters -> {top_overall}"
        )

    #Get hours spent in top5 clusters for week and weekend
    for name, df in clustered.items():
        week, weekend = weekday_weekend_stats(df)

        # Exclude noise cluster -1
        week = week[week['cluster'] != -1].head(5)
        weekend = weekend[weekend['cluster'] != -1].head(5)

        print(f"\n{name}:")
        if not week.empty and not weekend.empty:
            print("  Weekdays (hours spent in top clusters):")
            print(week[['cluster', 'hours']].to_string(index=False))
            print("  Weekends (hours spent in top clusters):")
            print(weekend[['cluster', 'hours']].to_string(index=False))
    
if __name__ == "__main__":
    # first run: set to True to compute + save clusters
    # later runs (for mapping/analysis only): change to False
    main(run_clustering=False)
