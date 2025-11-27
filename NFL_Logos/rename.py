import os
import re

FOLDER = "NFL_Logos"

# Matches "green-bay-packers-anything-else.png" and keeps "green-bay-packers"
pattern = re.compile(r"^([a-z-]+?)(?:-[^-]+)+\.png$", re.IGNORECASE)

for filename in os.listdir(FOLDER):
    match = pattern.match(filename)
    if match:
        team_name = match.group(1)  # "green-bay-packers"
        new_name = f"{team_name}.png"
        old_path = os.path.join(FOLDER, filename)
        new_path = os.path.join(FOLDER, new_name)

        if os.path.exists(new_path):
            print(f"⚠️ Skipping {filename}, {new_name} already exists.")
            continue

        os.rename(old_path, new_path)
        print(f"✅ Renamed: {filename} → {new_name}")
