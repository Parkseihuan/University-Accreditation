import re
import os
from pathlib import Path
import pdfplumber
import pandas as pd

# --- Configuration ---
# Use relative paths for portability
REPO_ROOT = Path(os.getcwd())
RAW_DIR = REPO_ROOT / "data" / "raw" / "3.1"
OUT_CSV = REPO_ROOT / "data" / "4th-cycle" / "3.1" / "faculty_numbers_2021_2025.csv"

def extract_year_from_filename(path: Path) -> int:
    # Example: "2021 정보공시.pdf" -> 2021
    m = re.search(r"20\d{2}", path.name)
    if not m:
        print(f"[WARN] Could not find year in filename: {path.name}")
        return 0
    return int(m.group())

def find_target_table(page) -> list[list[str]]:
    """
    Finds the table containing "Full-time Faculty Ratio" data.
    """
    text = page.extract_text() or ""
    # Keywords to identify the correct page/table
    # Adjust these based on the actual PDF content
    if "전임교원 1인당 학생 수" in text and "전임교원 확보율" in text:
        tables = page.extract_tables()
        if tables:
            return tables[0]  # Assuming the first table is the target
    return None

def parse_table_to_rows(year: int, table: list[list[str]]) -> list[dict]:
    """
    Parses the extracted table into structured rows.
    """
    if not table:
        return []

    header = table[0]
    rows = table[1:]
    result = []

    # Map column indices based on header names
    col_map = {}
    for idx, col in enumerate(header):
        col_str = str(col).replace("\n", "")
        if "전임교원" in col_str and "계" in col_str: # Assuming 'Total' column for Full-time
             col_map["전임교원수A"] = idx
        elif "겸임교원" in col_str:
             col_map["겸임교원수"] = idx
        elif "법정정원" in col_str and "학생정원" in col_str:
             col_map["법정정원_학생정원"] = idx
        elif "법정정원" in col_str and "재학생" in col_str:
             col_map["법정정원_재학생"] = idx
    
    # Fallback if column mapping fails (for testing with dummy data)
    if not col_map:
        # print("[DEBUG] Column mapping failed. Using default indices for testing.")
        # This is risky but useful if headers are complex. 
        # For now, let's try to be strict or provide a default if it looks like a standard table
        pass

    for row in rows:
        # Look for the "Total" or "University" row
        # Adjust "전체" to whatever the row label is in the PDF
        if row[0] and "전체" in str(row[0]):
            
            def to_int(x):
                if x is None: return 0
                clean_x = re.sub(r"[^\d]", "", str(x))
                return int(clean_x) if clean_x else 0

            # Use mapped indices or defaults
            idx_a = col_map.get("전임교원수A", 2) # Default index 2
            idx_adj = col_map.get("겸임교원수", 3) # Default index 3
            idx_b_std = col_map.get("법정정원_학생정원", 4) # Default index 4
            idx_b_enr = col_map.get("법정정원_재학생", 5) # Default index 5

            a = to_int(row[idx_a]) if len(row) > idx_a else 0
            adjunct = to_int(row[idx_adj]) if len(row) > idx_adj else 0
            b_student = to_int(row[idx_b_std]) if len(row) > idx_b_std else 0
            b_enrolled = to_int(row[idx_b_enr]) if len(row) > idx_b_enr else 0

            if a and b_student:
                result.append({
                    "연도": year,
                    "기준구분": "학생정원",
                    "전임교원수A": a,
                    "겸임교원수": adjunct,
                    "교원법정정원B": b_student,
                })
            if a and b_enrolled:
                result.append({
                    "연도": year,
                    "기준구분": "재학생",
                    "전임교원수A": a,
                    "겸임교원수": adjunct,
                    "교원법정정원B": b_enrolled,
                })
            break # Found the total row

    return result

def main():
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    all_rows = []
    # Process all PDFs in the raw directory
    pdf_files = list(RAW_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {RAW_DIR}")
        return

    for pdf_path in pdf_files:
        year = extract_year_from_filename(pdf_path)
        if year == 0: continue
        
        print(f"Processing {pdf_path.name}...")
        try:
            with pdfplumber.open(pdf_path) as pdf:
                target_table = None
                for page in pdf.pages:
                    table = find_target_table(page)
                    if table:
                        target_table = table
                        break
                
                if target_table is None:
                    print(f"[WARN] Target table not found in {pdf_path.name}")
                    continue

                rows = parse_table_to_rows(year, target_table)
                all_rows.extend(rows)
        except Exception as e:
            print(f"[ERROR] Failed to process {pdf_path.name}: {e}")

    if not all_rows:
        print("No data extracted.")
        return

    df = pd.DataFrame(all_rows)
    # Sort by Year and Basis
    df = df.sort_values(["연도", "기준구분"])
    
    df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"Successfully saved extracted data to {OUT_CSV}")

if __name__ == "__main__":
    main()
