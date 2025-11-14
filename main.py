import pandas as pd
import os

"""
Adding the locations through the sync function on Onedrive
should add a local copy to your pc. Make sure that Onedrive
is turned on when running the program
"""
locations_path = ""

#Collect the data from the csvs and store them in a list of dataframes
list_of_frames = []

for file in os.listdir(locations_path):
    path = os.path.join(locations_path, file)
    df = pd.read_csv(path, delimiter = ",")
    list_of_frames.append(df)

"""
Clean the data. This includes:
- checking accuracy data isn't missing (remove otherwise)
- checking accuracy doesn't pass the threshold: 1000
- removing data without full coordinates
- adding missing user_ids
- removing data without full dates
"""

