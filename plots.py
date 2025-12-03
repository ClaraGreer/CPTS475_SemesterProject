# plots.py
import pandas as pd
import matplotlib.pyplot as plt
import re
import os

REPORT_DIR = "reports"
PLOT_DIR = "plots"

os.makedirs(PLOT_DIR, exist_ok=True)

def plot_user_report(report_file: str, save_dir: str = PLOT_DIR):
    username = os.path.basename(report_file).replace("_report.txt", "")
    
    # Read the report
    with open(report_file, "r") as f:
        lines = f.readlines()
    
    # Extract month and hours per top cluster
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
    
    # Convert to DataFrame
    max_top = max(len(h) for h in month_data.values())
    df = pd.DataFrame.from_dict(
        month_data, orient="index", columns=[f"Top{i+1}" for i in range(max_top)]
    )
    df.index = pd.to_datetime(df.index)
    
    # ---- Line Plot ----
    plt.figure(figsize=(12,6))
    for col in df.columns:
        plt.plot(df.index, df[col], marker='o', label=col)
    plt.title(f"Hours Spent at Top {max_top} Locations per Month\n({username})")
    plt.xlabel("Month")
    plt.ylabel("Hours")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    lineplot_file = os.path.join(save_dir, f"{username}_lineplot.png")
    plt.savefig(lineplot_file)
    plt.close()
    
    print(f"Plots saved for {username}: {lineplot_file}")

# ---- Process all users ----
def plot_all_users(report_dir: str = REPORT_DIR, save_dir: str = PLOT_DIR):
    files = [f for f in os.listdir(report_dir) if f.endswith("_report.txt")]
    for f in files:
        plot_user_report(os.path.join(report_dir, f), save_dir)


