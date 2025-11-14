# clustering.py
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

def cluster_locations_per_month(df, eps_meters=50, min_samples=5, n_jobs=-1):
    """
    Cluster all locations grouped by month in parallel using DBSCAN with Haversine metric.

    Parameters:
    - df: DataFrame with 'datetime', 'latitude', 'longitude'
    - eps_meters: clustering radius in meters
    - min_samples: minimum points for a cluster
    - n_jobs: parallel jobs for DBSCAN
    """
    df = df.copy()
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['month'] = df['datetime'].dt.to_period('M')

    result_dfs = []

    for month, group in df.groupby('month'):
        if group.empty:
            continue

        # Convert coordinates to radians for Haversine metric
        coords = np.radians(group[['latitude', 'longitude']].to_numpy())

        # DBSCAN clustering
        db = DBSCAN(
            eps=eps_meters / 6371000,  # Convert meters to radians
            min_samples=min_samples,
            metric='haversine',
            n_jobs=n_jobs
        )
        labels = db.fit_predict(coords)

        group = group.copy()
        group['cluster'] = labels
        result_dfs.append(group)

    return pd.concat(result_dfs, ignore_index=True)


def compute_time_spent(df):
    """
    Compute time spent per cluster in hours.
    Assumes 'datetime' is sorted.
    """
    df = df.sort_values('datetime')
    df['time_diff'] = df['datetime'].diff().dt.total_seconds().fillna(0) / 3600  # hours
    time_per_cluster = df.groupby('cluster')['time_diff'].sum().reset_index()
    time_per_cluster.rename(columns={'time_diff': 'hours'}, inplace=True)
    return time_per_cluster
