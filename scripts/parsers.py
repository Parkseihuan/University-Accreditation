import pandas as pd
import os

def parse_fulltime_ratio(file_paths):
    """
    Parses Excel files for Full-time Faculty Ratio.
    Expected columns: Year, Count, Quota, Ratio, Note
    Returns a Markdown table string.
    """
    all_data = []
    for file_path in file_paths:
        try:
            df = pd.read_excel(file_path)
            all_data.append(df)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""

    if not all_data:
        return ""
        
    combined_df = pd.concat(all_data)
    # Sort by Year if possible
    if 'Year' in combined_df.columns:
        combined_df = combined_df.sort_values('Year')

    # Generate Markdown Table Rows
    lines = []
    for _, row in combined_df.iterrows():
        year = row.get('Year', '')
        count = row.get('Count', '')
        quota = row.get('Quota', '')
        ratio = row.get('Ratio', '')
        note = row.get('Note', '')
        
        # Apply 4th cycle color (Orange)
        line = f"| <span style=\"color: #ff7f0e;\">{year}</span> | <span style=\"color: #ff7f0e;\">{count}</span> | <span style=\"color: #ff7f0e;\">{quota}</span> | <span style=\"color: #ff7f0e;\">{ratio}</span> | <span style=\"color: #ff7f0e;\">{note}</span> |"
        lines.append(line)
        
    return "\n".join(lines)

def parse_new_hires(file_paths):
    """
    Parses Excel files for New Hires.
    Returns a Markdown table string.
    """
    # Placeholder implementation
    return "| <span style=\"color: #ff7f0e;\">2024</span> | <span style=\"color: #ff7f0e;\">10</span> | <span style=\"color: #ff7f0e;\">New Hires Data</span> |"
