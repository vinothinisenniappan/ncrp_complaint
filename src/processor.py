import re

def extract_fields(text):
    data = {}

    id_match = re.search(r'(Complaint ID|Ref No)[:\s]+(\w+)', text)
    amt_match = re.search(r'₹\s?([\d,]+)', text)

    data["Complaint ID"] = id_match.group(2) if id_match else None
    data["Amount Lost"] = amt_match.group(1).replace(',', '') if amt_match else 0

    if "upi" in text.lower():
        data["Platform"] = "UPI"
    elif "bank" in text.lower():
        data["Platform"] = "Banking"
    else:
        data["Platform"] = "Other"

    if "fraud" in text.lower():
        data["Crime Type"] = "Financial Fraud"
    elif "impersonation" in text.lower():
        data["Crime Type"] = "Impersonation"
    else:
        data["Crime Type"] = "Other"

    return data
