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

    # --- Read the report ---
    with open(report_file, "r") as f:
        lines = f.readlines()

    # --- Extract month and hours per top cluster ---
    month_data = {}
    for line in lines:
        match = re.match(r"(\d{4}-\d{2}): (.+)", line)
        if match:
            month = match.group(1)
            clusters = match.group(2).split(", ")
            hours = []
            for c in clusters:
                h_match = re.search(r"\(([\d\.]+)h\)", c)
                if h_match:
                    h = float(h_match.group(1))
                    hours.append(h)
            month_data[month] = hours

    if not month_data:
        print(f"No monthly data found for {username}")
        return

    # --- Convert to DataFrame ---
    max_top = max(len(h) for h in month_data.values())
    df_monthly = pd.DataFrame.from_dict(
        month_data, orient="index", columns=[f"Top{i+1}" for i in range(max_top)]
    )
    df_monthly.index = pd.to_datetime(df_monthly.index)

    # --- Extract weekday/weekend data ---
    weekday_line = [l for l in lines if l.startswith("Weekdays:")]
    weekend_line = [l for l in lines if l.startswith("Weekends:")]

    weekday_data = {}
    weekend_data = {}
    top_locations = [f"Top{i+1}" for i in range(max_top)]
    
    if weekday_line:
        parts = re.findall(r"([\d\.]+)\(([\d\.]+)h\)", weekday_line[0])
        for i, (c, h) in enumerate(parts):
            if i < max_top:
                weekday_data[top_locations[i]] = float(h)
    if weekend_line:
        parts = re.findall(r"([\d\.]+)\(([\d\.]+)h\)", weekend_line[0])
        for i, (c, h) in enumerate(parts):
            if i < max_top:
                weekend_data[top_locations[i]] = float(h)

    # --- Plot combined figure ---
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios':[2,1]})

    # Top panel: line plot
    ax = axs[0]
    for col in df_monthly.columns:
        ax.plot(df_monthly.index, df_monthly[col], marker='o', label=col)
    ax.set_facecolor("white")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)
    ax.set_ylabel("Hours")
    ax.set_title(f"{username} - Top Locations Over Time")
    ax.grid(False)

    # Bottom panel: weekday vs weekend bar plot
    ax2 = axs[1]
    x = range(len(top_locations))
    width = 0.35
    ax2.bar([i - width/2 for i in x], [weekday_data.get(loc, 0) for loc in top_locations], 
            width, label="Weekdays", color='steelblue')
    ax2.bar([i + width/2 for i in x], [weekend_data.get(loc, 0) for loc in top_locations], 
            width, label="Weekends", color='darkorange')
    ax2.set_xticks(x)
    ax2.set_xticklabels(top_locations)
    ax2.set_ylabel("Hours")
    ax2.set_title("Weekday vs Weekend Hours for Top Locations")
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(False)
    ax2.legend()

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
