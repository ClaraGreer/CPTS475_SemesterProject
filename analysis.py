# analysis.py
import pandas as pd
from clustering import compute_time_spent


def top_locations_monthly(df, n=5):
    df = df.copy()

    # Exclude noise cluster
    if "cluster" in df.columns:
        df = df[df["cluster"] != -1]

    df["month"] = df["datetime"].dt.to_period("M")
    monthly = {}
    for month, group in df.groupby("month"):
        dwell = compute_time_spent(group)

        # In case it's empty
        if dwell.empty:
            monthly[str(month)] = dwell
            continue

        # Take top n by hours
        dwell = dwell.sort_values("hours", ascending=False).head(n)
        monthly[str(month)] = dwell

    return monthly


def movement_transitions(df):
    df = df.copy()
    df = df.sort_values("datetime").reset_index(drop=True)

    df["next_cluster"] = df["cluster"].shift(-1)

    # Drop rows where next_cluster is NaN
    transitions = df.dropna(subset=["next_cluster"]).copy()

    # Exclude transitions involving noise (-1 -> anything, anything -> -1)
    transitions = transitions[
        (transitions["cluster"] != -1) & (transitions["next_cluster"] != -1)
    ]

    if transitions.empty:
        return pd.DataFrame(columns=["cluster", "next_cluster", "count"])

    return (
        transitions.groupby(["cluster", "next_cluster"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )


def weekday_weekend_stats(df):
    df = df.copy()

    # Exclude noise cluster
    if "cluster" in df.columns:
        df = df[df["cluster"] != -1]

    df["weekday"] = df["datetime"].dt.dayofweek
    df["is_weekend"] = df["weekday"].isin([5, 6])

    week = compute_time_spent(df.loc[df["is_weekend"] == False])
    weekend = compute_time_spent(df.loc[df["is_weekend"] == True])

    return week, weekend
