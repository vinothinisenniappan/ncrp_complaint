import pandas as pd
import pdfplumber

def read_csv(path):
    return pd.read_csv(path)

def read_excel(path):
    return pd.read_excel(path)

def read_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()
    return text
