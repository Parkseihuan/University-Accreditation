import pandas as pd
import os

os.makedirs("data/4th-cycle/3.1", exist_ok=True)

# Define the new format
data = {
    "연도": [2021, 2021, 2022, 2022, 2023, 2023, 2024, 2024, 2025, 2025],
    "기준구분": ["학생정원", "재학생", "학생정원", "재학생", "학생정원", "재학생", "학생정원", "재학생", "학생정원", "재학생"],
    "전임교원수A": [279, 279, 285, 285, 290, 290, 300, 300, 310, 310],
    "겸임교원수": [33, 33, 35, 35, 40, 40, 45, 45, 50, 50],
    "교원법정정원B": [386, 379, 386, 375, 386, 370, 386, 365, 386, 360]
}

df = pd.DataFrame(data)
df.to_excel("data/4th-cycle/3.1/faculty_numbers_2021_2025.xlsx", index=False)
print("Created dummy Excel file: data/4th-cycle/3.1/faculty_numbers_2021_2025.xlsx")
