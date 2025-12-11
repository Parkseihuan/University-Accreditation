import pandas as pd
import os

os.makedirs("data/4th-cycle/3.1", exist_ok=True)

data = {
    "Year": [2024, 2025],
    "Count": [120, 125],
    "Quota": [150, 150],
    "Ratio": [80.0, 83.3],
    "Note": ["4주기 자료", "4주기 자료"]
}

df = pd.DataFrame(data)
df.to_excel("data/4th-cycle/3.1/fulltime_ratio_2023_2025.xlsx", index=False)
print("Created dummy Excel file.")
