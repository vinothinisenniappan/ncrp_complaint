from extractor import read_pdf
from processor import extract_fields
from writer import write_to_excel
import pandas as pd
from pathlib import Path

OUTPUT_FILE = Path("../output/master_complaints.xlsx")

if OUTPUT_FILE.exists():
    existing = pd.read_excel(OUTPUT_FILE)
else:
    existing = pd.DataFrame()

text = read_pdf("../input_files/complaints.pdf")
data = extract_fields(text)

if data["Complaint ID"] not in existing.get("Complaint ID", []):
    write_to_excel(data, OUTPUT_FILE)
    print("Complaint added successfully")
else:
    print("Duplicate complaint detected")
