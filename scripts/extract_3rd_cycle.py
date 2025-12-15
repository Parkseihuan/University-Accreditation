import pdfplumber
import os

PDF_PATH = "3주기 - 대학자체진단평가보고서_ 교원 및 직원.pdf"
OUTPUT_TXT = "temp_3rd_cycle_content.txt"

def extract_content():
    if not os.path.exists(PDF_PATH):
        print(f"File not found: {PDF_PATH}")
        return

    with pdfplumber.open(PDF_PATH) as pdf:
        with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
            for i, page in enumerate(pdf.pages):
                f.write(f"--- Page {i+1} ---\n")
                
                # Extract Text
                text = page.extract_text()
                if text:
                    f.write(text)
                    f.write("\n\n")
                
                # Extract Tables (Simple)
                tables = page.extract_tables()
                for table in tables:
                    f.write("[TABLE START]\n")
                    for row in table:
                        # Clean None values
                        clean_row = [str(cell).replace('\n', ' ') if cell is not None else "" for cell in row]
                        f.write(" | ".join(clean_row))
                        f.write("\n")
                    f.write("[TABLE END]\n\n")

    print(f"Extracted content to {OUTPUT_TXT}")

if __name__ == "__main__":
    extract_content()
