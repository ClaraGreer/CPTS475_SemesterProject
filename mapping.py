# mapping.py
import os
import folium
import pandas as pd

def make_maps_for_user(user_name: str, df: pd.DataFrame, output_dir: str = "maps"):
    """
    Generate interactive maps for a user's clustered GPS data.

    Produces:
      - One overall map of all clusters.
      - One map per month showing points colored by cluster.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Ensure datetime is proper
    if not pd.api.types.is_datetime64_any_dtype(df["datetime"]):
        df["datetime"] = pd.to_datetime(df["datetime"])

    # Filter out noise cluster if using -1 as noise
    df_non_noise = df[df["cluster"] != -1].copy()
    if df_non_noise.empty:
        print(f"  [mapping] No non-noise points for {user_name}, skipping maps.")
        return

    # Overall center of map
    center_lat = df_non_noise["latitude"].mean()
    center_lon = df_non_noise["longitude"].mean()

    # === 1. Overall map of all clusters ===
    overall_map = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    # Simple color palette
    colors = [
        "red", "blue", "green", "purple", "orange",
        "darkred", "lightred", "beige", "darkblue",
        "darkgreen", "cadetblue", "darkpurple", "white",
        "pink", "lightblue", "lightgreen", "gray", "black"
    ]

    cluster_ids = sorted(c for c in df_non_noise["cluster"].unique() if c != -1)
    color_map = {cid: colors[i % len(colors)] for i, cid in enumerate(cluster_ids)}

    for _, row in df_non_noise.iterrows():
        cid = row["cluster"]
        color = color_map.get(cid, "gray")
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=3,
            popup=f"Cluster {cid}<br>{row['datetime']}",
            fill=True,
            fill_opacity=0.7,
            opacity=0.7,
            color=color,
        ).add_to(overall_map)

    overall_path = os.path.join(output_dir, f"{user_name}_all_clusters.html")
    overall_map.save(overall_path)
    print(f"  [mapping] Saved overall cluster map: {overall_path}")

    # === 2. Monthly maps ===
    df_non_noise["year_month"] = df_non_noise["datetime"].dt.to_period("M").astype(str)

    for ym, month_df in df_non_noise.groupby("year_month"):
        if month_df.empty:
            continue

        m_center_lat = month_df["latitude"].mean()
        m_center_lon = month_df["longitude"].mean()

        month_map = folium.Map(location=[m_center_lat, m_center_lon], zoom_start=12)

        month_clusters = sorted(month_df["cluster"].unique())
        month_color_map = {
            cid: colors[i % len(colors)] for i, cid in enumerate(month_clusters)
        }

        for _, row in month_df.iterrows():
            cid = row["cluster"]
            color = month_color_map.get(cid, "gray")
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=3,
                popup=f"Cluster {cid}<br>{row['datetime']}",
                fill=True,
                fill_opacity=0.7,
                opacity=0.7,
                color=color,
            ).add_to(month_map)

        month_path = os.path.join(output_dir, f"{user_name}_{ym}.html")
        month_map.save(month_path)
        print(f"  [mapping] Saved monthly map for {ym}: {month_path}")
