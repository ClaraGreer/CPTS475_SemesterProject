# plots.py
import pandas as pd
import matplotlib.pyplot as plt
import re
import os

REPORT_DIR = "reports"
PLOT_DIR = "plots"
os.makedirs(PLOT_DIR, exist_ok=True)

def plot_user_combined(report_file: str, save_dir: str = PLOT_DIR):
    username = os.path.basename(report_file).replace("_report.txt", "")

    # --- Read report ---
    with open(report_file, "r") as f:
        lines = f.readlines()

    # --- Extract summary metrics ---
    total_points = non_noise = noise = clusters = None
    for line in lines:
        L = line.lower()
        if "total points" in L:
            total_points = re.search(r"(\d[\d,]*)", line).group(1)
        elif "non-noise" in L:
            non_noise = re.search(r"(\d[\d,]*)", line).group(1)
        elif "noise points" in L:
            noise = re.search(r"(\d[\d,]*)", line).group(1)
        elif "detected clusters" in L or "clusters detected" in L:
            clusters = re.search(r"(\d+)", line).group(1)

    summary_table = [
        ["Total Points", total_points],
        ["Non-Noise Points", non_noise],
        ["Noise Points", noise],
        ["Detected Clusters", clusters],
    ]

    # --- Extract monthly data ---
    month_data = {}
    month_cluster_ids = {}
    for line in lines:
        match = re.match(r"(\d{4}-\d{2}): (.+)", line)
        if match:
            month = match.group(1)
            clusters_str = match.group(2).split(", ")
            hours = []
            cids = []
            for c in clusters_str:
                h_match = re.search(r"\(([\d\.]+)h\)", c)
                cid_match = re.match(r"([\d\.]+)\(", c)
                if h_match:
                    hours.append(float(h_match.group(1)))
                if cid_match:
                    cids.append(cid_match.group(1))
            month_data[month] = hours
            month_cluster_ids[month] = cids

    if not month_data:
        print(f"No monthly data found for {username}")
        return

    max_top = max(len(h) for h in month_data.values())
    df_monthly = pd.DataFrame.from_dict(
        month_data, orient="index", columns=[f"Top{i+1}" for i in range(max_top)]
    )
    df_monthly.index = pd.to_datetime(df_monthly.index)

    # --- Map Top columns to most frequent cluster IDs ---
    top_clusters_per_col = []
    for i in range(max_top):
        col_values = []
        for cids in month_cluster_ids.values():
            if i < len(cids):
                col_values.append(cids[i])
        top_clusters_per_col.append(pd.Series(col_values).mode()[0] if col_values else f"Top{i+1}")

    # --- Extract weekday/weekend data ---
    weekday_line = [l for l in lines if l.startswith("Weekdays:")]
    weekend_line = [l for l in lines if l.startswith("Weekends:")]

    weekday_parts = re.findall(r"([\d\.]+)\(([\d\.]+)h\)", weekday_line[0]) if weekday_line else []
    weekend_parts = re.findall(r"([\d\.]+)\(([\d\.]+)h\)", weekend_line[0]) if weekend_line else []

    weekday_dict = {cid: float(h) for cid, h in weekday_parts}
    weekend_dict = {cid: float(h) for cid, h in weekend_parts}

    cluster_ids = sorted(set(weekday_dict.keys()) | set(weekend_dict.keys()), key=float)
    wd_hours = [weekday_dict.get(cid, 0) for cid in cluster_ids]
    we_hours = [weekend_dict.get(cid, 0) for cid in cluster_ids]

        # --- Create figure ---
    fig, axs = plt.subplots(
        3, 1, figsize=(14, 10),
        gridspec_kw={'height_ratios': [2.2, 1.3, 0.9]}
    )

    # --- Big overarching title ---
    fig.suptitle(f"User: {username}", fontsize=20, fontweight='bold')

    # --- Row 1: Monthly line plot with cluster IDs ---
    ax = axs[0]
    for idx, col in enumerate(df_monthly.columns):
        cluster_label = top_clusters_per_col[idx]
        ax.plot(df_monthly.index, df_monthly[col], marker='o', label=f"Cluster {cluster_label}")

    ax.set_facecolor("white")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel("Hours")
    ax.set_title("Top Locations Over Time")
    ax.grid(False)
    ax.legend(title="Cluster ID", bbox_to_anchor=(1.02, 1), loc='upper left')

    # --- Optional horizontal line (border) below this plot ---
    ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='--', alpha=0.5)

    # --- Row 2: Weekday vs Weekend bar plot ---
    ax2 = axs[1]
    x = range(len(cluster_ids))
    ax2.bar([i - 0.2 for i in x], wd_hours, width=0.4, label="Weekdays", color="#614AE3")
    ax2.bar([i + 0.2 for i in x], we_hours, width=0.4, label="Weekends", color="#DE3BC5")
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(cluster_ids, rotation=45)
    ax2.set_xlabel("Cluster ID")
    ax2.set_ylabel("Hours")
    ax2.set_title("Weekday vs Weekend Hours by Cluster")
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.legend(title="Day Type", loc='upper left', bbox_to_anchor=(1.02, 1))

    # Label bars
    for idx, hrs in enumerate(wd_hours):
        ax2.text(idx - 0.2, hrs + 0.02, f"{hrs:.0f}", ha="center", fontsize=8)
    for idx, hrs in enumerate(we_hours):
        ax2.text(idx + 0.2, hrs + 0.02, f"{hrs:.0f}", ha="center", fontsize=8)

    # Optional horizontal line (border) below bar plot
    ax2.axhline(y=0, color='gray', linewidth=0.5, linestyle='--', alpha=0.5)

    # --- Row 3: Summary table at the bottom ---
    ax0 = axs[2]
    ax0.set_axis_off()
    ax0.set_title("Summary Data")
    table = ax0.table(
        cellText=summary_table,
        colLabels=["Metrics", "Value"],
        loc="center",
        cellLoc="left"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.3)

    # --- Adjust layout to fit suptitle ---
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # leave top space for suptitle

    plt.tight_layout()
    combined_file = os.path.join(save_dir, f"{username}_combined_plot.png")
    plt.savefig(combined_file)
    plt.close()
    print(f"Combined plot saved for {username}: {combined_file}")



# ---- Process all users ----
def plot_user_report(report_dir: str = REPORT_DIR, save_dir: str = PLOT_DIR):
    files = [f for f in os.listdir(report_dir) if f.endswith("_report.txt")]
    for f in files:
        plot_user_combined(os.path.join(report_dir, f), save_dir)
