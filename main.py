# main.py
import os
import pandas as pd
from IPython.display import display
from data_load import load_all_csvs, clean_gps
from clustering import cluster_locations_per_month, compute_time_spent
from analysis import top_locations_monthly, movement_transitions, weekday_weekend_stats
from mapping import make_maps_for_user

CLUSTERED_DIR = "clustered_outputs"
REPORT_DIR = "reports"

# === MAP GENERATION SETTINGS ===
GENERATE_SPECIFIC_CLUSTERS = True
SPECIFIC_CLUSTER_MODE = "overall_top"
MANUAL_CLUSTERS = [33, 17, 36]  # only used if SPECIFIC_CLUSTER_MODE == "manual"


<<<<<<< HEAD
# ------------ WRITE REPORT FILES ------------
def save_user_report(username, top5_monthly, week_stats, weekend_stats, transitions, summary_info):
    os.makedirs(REPORT_DIR, exist_ok=True)
    path = os.path.join(REPORT_DIR, f"{username}_report.txt")

    with open(path, "w", encoding="utf-8") as f:

        f.write(f"==== Report for {username} ====\n\n")

        # Summary section
        f.write("=== Summary ===\n")
        f.write(f"Total points: {summary_info['total_points']}\n")
        f.write(f"Non-noise points: {summary_info['non_noise']}\n")
        f.write(f"Noise points: {summary_info['noise']}\n")
        f.write(f"Detected clusters: {summary_info['n_clusters']}\n")
        f.write(f"Top overall clusters: {summary_info['top_overall']}\n\n")

        # Monthly top 5 locations
        f.write("=== Top 5 Locations Per Month ===\n")
        for month, df in top5_monthly.items():
            f.write(f"\nMonth: {month}\n")
            f.write(df[['cluster', 'hours']].head(5).to_string(index=False))
            f.write("\n")

        # Weekday / Weekend
        f.write("\n=== Weekday vs Weekend Time Spent ===\n\n")

        f.write("Weekdays:\n")
        if not week_stats.empty:
            f.write(week_stats[['cluster', 'hours']].to_string(index=False) + "\n")
        else:
            f.write("No weekday clusters.\n\n")

        f.write("\nWeekends:\n")
        if not weekend_stats.empty:
            f.write(weekend_stats[['cluster', 'hours']].to_string(index=False) + "\n")
        else:
            f.write("No weekend clusters.\n\n")

        # Transitions
        f.write("\n=== Movement Transitions (first 10 rows) ===\n")
        if not transitions.empty:
            f.write(transitions.head(10).to_string(index=False) + "\n")
        else:
            f.write("No transitions detected.\n")

        f.write("\n==== END OF REPORT ====\n")

    print(f"[✓] Saved report → {path}")


# ------------ MAIN PROGRAM ------------
def main(run_clustering: bool = True):
=======
def main(run_clustering: bool = False, run_mapping: bool = False):
>>>>>>> 01d09d90cd3f73f33daf5fd638b2b13daa8872e9
    print("\n=== Loading CSV Files ===\n")
    datasets = load_all_csvs()

    print("\n=== Cleaning Data ===\n")
    cleaned = {}
    for name, df in datasets.items():
        clean_df = clean_gps(df)
        clean_df["datetime"] = pd.to_datetime(clean_df["datetime"])
        cleaned[name] = clean_df
        print(f"{name}: {clean_df.shape[0]} rows remain after cleaning")

    os.makedirs(CLUSTERED_DIR, exist_ok=True)
    clustered = {}

    # Run clustering
    if run_clustering:
        print("\n=== Clustering Locations Per Month ===\n")
        for name, df in cleaned.items():
            cluster_df = cluster_locations_per_month(
                df, eps_meters=50, min_samples=5, n_jobs=-1
            )
            clustered[name] = cluster_df

            # save clustered csv
            out_path = os.path.join(CLUSTERED_DIR, f"{name}_clustered.csv")
            cluster_df.to_csv(out_path, index=False)

            total_points = len(cluster_df)
            noise_points = (cluster_df["cluster"] == -1).sum()
            non_noise = total_points - noise_points
            n_clusters = cluster_df["cluster"].nunique() - (1 if -1 in cluster_df["cluster"].unique() else 0)

            print(
                f"{name}: {n_clusters} clusters, "
                f"{non_noise}/{total_points} non-noise points (saved to {out_path})"
            )
    else:
        print("\n=== Loading PRE-COMPUTED Clustered Data ===\n")
        for name in cleaned.keys():
            path = os.path.join(CLUSTERED_DIR, f"{name}_clustered.csv")
            if not os.path.exists(path):
                raise FileNotFoundError(f"Clustered file missing: {path}")
            df = pd.read_csv(path, parse_dates=["datetime"])
            clustered[name] = df
            print(f"{name}: loaded {df.shape[0]} rows from {path}")

    # -------------------------------------------------
    # WRITE REPORTS INSTEAD OF PRINTING EVERYTHING
    # -------------------------------------------------
    print("\n=== Generating Reports ===\n")

    for name, df in clustered.items():

        # Top 5 monthly
        top5_monthly = top_locations_monthly(df, n=5)

        # Weekday vs Weekend
        week, weekend = weekday_weekend_stats(df)
        week = week[week['cluster'] != -1].head(5)
        weekend = weekend[weekend['cluster'] != -1].head(5)

        # Transitions
        transitions = movement_transitions(df)

        # Summary info
        cluster_hours = compute_time_spent(df)
        cluster_hours = cluster_hours[cluster_hours['cluster'] != -1]
        top_overall = cluster_hours.head(5)['cluster'].tolist()

<<<<<<< HEAD
        summary_info = {
            "total_points": len(df),
            "non_noise": (df["cluster"] != -1).sum(),
            "noise": (df["cluster"] == -1).sum(),
            "n_clusters": df["cluster"].nunique() - (1 if -1 in df["cluster"].unique() else 0),
            "top_overall": top_overall
        }

        # Save report file
        save_user_report(
            username=name,
            top5_monthly=top5_monthly,
            week_stats=week,
            weekend_stats=weekend,
            transitions=transitions,
            summary_info=summary_info
        )

    # ---- Map generation ----
    print("\n=== Generating Maps ===\n")

    top5_clusters = {}
    for name, df in clustered.items():
        t5 = top_locations_monthly(df, n=5)
        top5_clusters[name] = {month: v["cluster"].tolist() for month, v in t5.items()}

    top5_dated = {}
    top_overall_clusters = {}

    for name, df in clustered.items():
        newdf = df.copy()
        newdf["month"] = newdf["datetime"].dt.to_period("M")
        newdf = newdf[newdf["cluster"] != -1]
        valid_months = [pd.Period(m) for m in top5_clusters[name].keys()]
        newdf = newdf[newdf["month"].isin(valid_months)]
=======
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
>>>>>>> 01d09d90cd3f73f33daf5fd638b2b13daa8872e9

            def get_top5(group):
                month_str = str(group.name)
                top_clusters = top5_clusters[name].get(month_str, [])
                return group[group["cluster"].isin(top_clusters)]

<<<<<<< HEAD
        newdf = newdf.groupby("month", group_keys=False).apply(get_top5)
        top5_dated[name] = newdf

        all_top = []
        for month_clusters in top5_clusters[name].values():
            all_top.extend(month_clusters)
        all_unique = list(dict.fromkeys(all_top))
        top_overall_clusters[name] = all_unique[:5]

    def make_maps_for_specific_clusters(user: str, df: pd.DataFrame, clusters: list[int]):
        df_filtered = df[df["cluster"].isin(clusters)]
        if df_filtered.empty:
            print(f"No points found for clusters {clusters} in {user}.")
            return
        make_maps_for_user(user, df_filtered)
        print(f"Map generated for {user}, clusters {clusters}.")

    # Map loop
    for name, df in top5_dated.items():
        if GENERATE_SPECIFIC_CLUSTERS:
            if SPECIFIC_CLUSTER_MODE == "overall_top":
                clusters_to_map = top_overall_clusters[name]
            else:
                clusters_to_map = MANUAL_CLUSTERS
            make_maps_for_specific_clusters(name, df, clusters_to_map)
        else:
=======
            newdf = newdf.groupby("month", group_keys=False).apply(get_top5)

            top5_dated[name] = newdf

        # Generate the top 5 location maps for each person
        for name, df in top5_dated.items():
            print(f"Generating maps for {name}...")
>>>>>>> 01d09d90cd3f73f33daf5fd638b2b13daa8872e9
            make_maps_for_user(name, df)


<<<<<<< HEAD
=======
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
    
>>>>>>> 01d09d90cd3f73f33daf5fd638b2b13daa8872e9
if __name__ == "__main__":
    # first run: set to True to compute + save clusters
    # later runs (for mapping/analysis only): change to False
    main(run_clustering=False)
