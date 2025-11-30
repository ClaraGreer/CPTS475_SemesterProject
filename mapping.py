# mapping.py
import os
import folium
import pandas as pd
from typing import Optional


def make_maps_for_user(
    user_name: str,
    df: pd.DataFrame,
    centroids: Optional[pd.DataFrame] = None,
    output_dir: str = "maps",
    max_points_overall: int = 20000,
    max_points_per_month: int = 5000,
):
    """
    Generate one HTML with all months as tabs.
    """
    os.makedirs(output_dir, exist_ok=True)

    if not pd.api.types.is_datetime64_any_dtype(df["datetime"]):
        df["datetime"] = pd.to_datetime(df["datetime"])

    df_non_noise = df[df["cluster"] != -1].copy()
    if df_non_noise.empty:
        print(f"[mapping] No non-noise points for {user_name}, skipping maps.")
        return

    # Downscale overall
    if len(df_non_noise) > max_points_overall:
        df_non_noise = df_non_noise.sample(max_points_overall, random_state=0)

    df_non_noise["year_month"] = df_non_noise["datetime"].dt.to_period("M").astype(str)
    months = sorted(df_non_noise["year_month"].unique())

    # Create a separate Folium map for each month
    month_maps_html = {}
    colors = [
        "red", "blue", "green", "purple", "orange",
        "darkred", "lightred", "beige", "darkblue",
        "darkgreen", "cadetblue", "darkpurple", "white",
        "pink", "lightblue", "lightgreen", "gray", "black",
    ]

    for ym in months:
        month_df = df_non_noise[df_non_noise["year_month"] == ym].copy()
        if len(month_df) > max_points_per_month:
            month_df = month_df.sample(max_points_per_month, random_state=0)

        center_lat = month_df["latitude"].mean()
        center_lon = month_df["longitude"].mean()
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

        cluster_ids = sorted(month_df["cluster"].unique())
        color_map = {cid: colors[i % len(colors)] for i, cid in enumerate(cluster_ids)}

        for _, row in month_df.iterrows():
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
            ).add_to(m)

        if centroids is not None and not centroids.empty:
            month_centroids = centroids[centroids["cluster"].isin(cluster_ids)]
            for _, row in month_centroids.iterrows():
                cid = row["cluster"]
                folium.Marker(
                    location=[row["centroid_lat"], row["centroid_lon"]],
                    popup=f"Cluster {cid} (centroid)",
                    tooltip=f"Cluster {cid} (centroid)",
                ).add_to(m)

        month_maps_html[ym] = m._repr_html_()  # store HTML as string

    # Create final HTML with tabs
    tab_headers = "".join(
        f'<li class="nav-item"><a class="nav-link {"active" if i==0 else ""}" data-bs-toggle="tab" href="#tab{i}">{m}</a></li>'
        for i, m in enumerate(months)
    )
    tab_contents = "".join(
        f'<div class="tab-pane fade {"show active" if i==0 else ""}" id="tab{i}">{month_maps_html[m]}</div>'
        for i, m in enumerate(months)
    )

    final_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>{user_name} Monthly Maps</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/js/bootstrap.bundle.min.js"></script>
    <style>html, body {{height:100%; margin:0; padding:0;}}</style>
    </head>
    <body>
    <div class="container-fluid">
      <h2>{user_name} Monthly Maps</h2>
      <ul class="nav nav-tabs">{tab_headers}</ul>
      <div class="tab-content" style="height:90vh;">{tab_contents}</div>
    </div>
    </body>
    </html>
    """

    out_path = os.path.join(output_dir, f"{user_name}_monthly_tabs.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"[mapping] Saved tabbed monthly map: {out_path}")