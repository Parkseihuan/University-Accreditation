import os
import pandas as pd
import re
import argparse
# from google import generativeai as genai # Commented out as we don't have API key yet

# --- Configuration ---
DATA_PATH = "data/4th-cycle/3.1/faculty_numbers_2021_2025.csv"
MD_PATH = "criteria/3.1-교원-확보-및-구성/3.1-교원-확보-및-구성.md"

# --- Utils ---
def calc_ratios(df: pd.DataFrame):
    """
    Calculates ratios based on 4th cycle handbook formulas.
    """
    df = df.copy()
    # A(%) = Full-time / Quota * 100
    df["A_fulltime_pct"] = df["전임교원수A"] / df["교원법정정원B"] * 100
    # B(%) = Adjunct / Quota * 100
    df["B_adjunct_pct"] = df["겸임교원수"] / df["교원법정정원B"] * 100
    
    # Combined = A + min(0.3 * B, 4.0)
    # Note: The formula is A + min(0.3*B, 4.0). 
    # Wait, the advice says: "A + min(0.3 * B, 4.0)"
    # But usually it means the *contribution* of B is capped at 4.0%? 
    # Or the *total* is capped?
    # "전임+겸임 확보율 = A + min(0.3 x B, 4.0)" -> This implies the adjunct contribution is capped at 4.0%.
    # Let's verify. Yes, usually adjuncts can contribute up to 20% of the quota, or specific % points.
    # The advice text says: "min(0.3 * B, 4.0)". So 0.3*B cannot exceed 4.0.
    
    df["adjunct_contribution"] = (0.3 * df["B_adjunct_pct"]).clip(upper=4.0)
    df["combined_pct"] = df["A_fulltime_pct"] + df["adjunct_contribution"]

    # Detail table: Year x Basis
    detail = df.sort_values(["연도", "기준구분"])

    # Final table: Min of (Student Quota, Enrolled Students) per Year
    final = (
        df.loc[:, ["연도", "기준구분", "combined_pct"]]
        .sort_values(["연도", "combined_pct"]) # Sort by pct ascending to get min first
        .groupby("연도")
        .first()
        .reset_index()
    )
    final = final.rename(columns={"combined_pct": "final_combined_pct",
                                  "기준구분": "final_basis"})
    return detail, final

def replace_between_markers(text: str, start_marker: str, end_marker: str, new_block: str) -> str:
    pattern = f"({re.escape(start_marker)})(.*?)({re.escape(end_marker)})"
    replacement = f"\\1\n{new_block.strip()}\n\\3"
    return re.sub(pattern, replacement, text, flags=re.DOTALL)

def call_gemini_placeholder(prompt: str) -> str:
    # Placeholder for LLM call
    return "\n> [AI 분석 결과 예시]\n> 전임교원 확보율이 지속적으로 상승하고 있으며, 특히 2024년에는 기준값 64%를 크게 상회하는 성과를 보였습니다.\n"

# --- Main Logic ---
def update_tables():
    if not os.path.exists(DATA_PATH):
        print(f"Data file not found: {DATA_PATH}")
        return "", "", ""
        
    df = pd.read_csv(DATA_PATH)
    detail, final = calc_ratios(df)

    # (1) Detail Table HTML
    rows = []
    for _, row in detail.iterrows():
        year = int(row["연도"])
        basis = row["기준구분"]
        a = row["A_fulltime_pct"]
        b = row["B_adjunct_pct"]
        c = row["combined_pct"]
        rows.append(f"| {year} | {basis} | {a:.2f} | {b:.2f} | {c:.2f} |")
    
    detail_table = "| 연도 | 기준구분 | 전임 A(%) | 겸임 B(%) | A+min(0.3B,4.0)(%) |\n|---|---|---|---|---|\n" + "\n".join(rows)

    # (2) 3rd Cycle Rows (2021-2023)
    rows_3rd = []
    # (3) 4th Cycle Rows (2024-2025)
    rows_4th = []
    
    for _, row in final.iterrows():
        year = int(row["연도"])
        val = row["final_combined_pct"]
        basis = row["final_basis"]
        status = '기준값 충족' if val >= 64 else '기준값 미충족'
        
        if year <= 2023:
            color = "#1f77b4" # Blue
            row_html = f"""    <tr>
      <td><span style="color:{color};">{year}</span></td>
      <td><span style="color:{color};">{val:.2f}</span></td>
      <td><span style="color:{color};">{status}</span></td>
      <td><span style="color:{color};">{basis} 기준 사용</span></td>
    </tr>"""
            rows_3rd.append(row_html)
        else:
            color = "#ff7f0e" # Orange
            row_html = f"""    <tr>
      <td><span style="color:{color};">{year}</span></td>
      <td><span style="color:{color};">{val:.2f}</span></td>
      <td><span style="color:{color};">{status}</span></td>
      <td><span style="color:{color};">{basis} 기준 사용</span></td>
    </tr>"""
            rows_4th.append(row_html)

    return detail_table, "\n".join(rows_3rd), "\n".join(rows_4th)

def update_text_blocks(detail_table: str, rows_3rd: str, rows_4th: str):
    if not os.path.exists(MD_PATH):
        print(f"Markdown file not found: {MD_PATH}")
        return

    with open(MD_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    # Update Detail Table
    text = replace_between_markers(text, "<!-- AUTO-GEN:3.1-DETAIL-RATIO-TABLE-START -->", "<!-- AUTO-GEN:3.1-DETAIL-RATIO-TABLE-END -->", detail_table)
    
    # Update 3rd Cycle Rows
    text = replace_between_markers(text, "<!-- AUTO-GEN:3.1-RATIO-3RD-START -->", "<!-- AUTO-GEN:3.1-RATIO-3RD-END -->", rows_3rd)
    
    # Update 4th Cycle Rows
    text = replace_between_markers(text, "<!-- AUTO-GEN:3.1-RATIO-4TH-START -->", "<!-- AUTO-GEN:3.1-RATIO-4TH-END -->", rows_4th)
    
    # Update Analysis (Placeholder)
    analysis_text = call_gemini_placeholder("analysis prompt")
    text = replace_between_markers(text, "<!-- AUTO-GEN:3.1-ANALYSIS-START -->", "<!-- AUTO-GEN:3.1-ANALYSIS-END -->", f'<span style="color:#ff7f0e;">{analysis_text}</span>')
    
    # Update Improvement (Placeholder)
    improvement_text = call_gemini_placeholder("improvement prompt")
    text = replace_between_markers(text, "<!-- AUTO-GEN:3.1-IMPROVEMENT-START -->", "<!-- AUTO-GEN:3.1-IMPROVEMENT-END -->", f'<span style="color:#ff7f0e;">{improvement_text}</span>')

    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Updated {MD_PATH}")

def main():
    detail_table, rows_3rd, rows_4th = update_tables()
    if detail_table:
        update_text_blocks(detail_table, rows_3rd, rows_4th)

if __name__ == "__main__":
    main()
