# analysis.py
def top_locations_monthly(df, n=5):
    df = df.copy()
    df["month"] = df["datetime"].dt.to_period("M")
    monthly = {}
    for month, group in df.groupby("month"):
        from clustering import compute_time_spent
        monthly[str(month)] = compute_time_spent(group).head(n)
    return monthly


def movement_transitions(df):
    df = df.copy()
    df["next_cluster"] = df["cluster"].shift(-1)
    transitions = df.dropna(subset=["next_cluster"])
    return transitions.groupby(["cluster", "next_cluster"]).size().reset_index(name="count")


def weekday_weekend_stats(df):
    df = df.copy()
    df["weekday"] = df["datetime"].dt.dayofweek
    df["is_weekend"] = df["weekday"].isin([5, 6])
    from clustering import compute_time_spent
    week = compute_time_spent(df[df["is_weekend"] == False])
    weekend = compute_time_spent(df[df["is_weekend"] == True])
    return week, weekend
