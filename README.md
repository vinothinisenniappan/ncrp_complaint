# NCRP Complaint Organizer & Case View System

A local web-based tool that converts raw NCRP complaint files into searchable, categorized, and duplicate-aware Excel registers, making it easier for police officers to find, track, and manage complaints.

## ⚠️ Disclaimer

**This system is NOT a replacement for the real NCRP portal.**
- It does NOT access or scrape any government website
- It works only with dummy/sample data and uploaded files
- It is meant purely for demonstration and workflow improvement
- All data is stored locally and processed offline

## 🎯 Project Goal

Demonstrate how NCRP complaints can be:
- Collected (via files or a sample form)
- Automatically structured
- Categorized into multiple Excel sheets
- De-duplicated and organized for easy investigation

## 🧩 Core Features

### 1. Dual Complaint Input
- **Method A (Main)**: Upload CSV, Excel, or PDF files
- **Method B (Demo)**: Sample web complaint form (for demonstration only)

### 2. Data Normalization
All complaints are normalized into a standard NCRP-style structure:
- Complaint ID / Acknowledgement Number
- Complaint Date & Incident Date
- Complainant details (name, mobile, email, district)
- Crime type (UPI fraud, harassment, job scam, etc.)
- Platform (UPI, bank, card, social media, OTP, etc.)
- Amount lost
- Police station / district
- Current status

### 3. Master Excel Register
- Single source of truth
- Appends new complaints without overwriting old data

### 4. Categorized Sheets
Automatically generates:
- **Sheet 1**: All Complaints (master)
- **Sheet 2**: Crime-Type-wise complaints
- **Sheet 3**: Platform-wise complaints
- **Sheet 4**: High-value complaints (above configurable amount)
- **Sheet 5**: Possible duplicate / linked complaints

### 5. Duplicate Detection
- Same Complaint ID
- Same phone/email + similar date & amount
- Flagged as "Possible duplicate" (not deleted)

## 🛠️ Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## 📁 Project Structure

```
NCRP_Complaint/
├── app.py                 # Main Flask application
├── data_processor.py      # Data normalization and processing
├── excel_generator.py     # Excel file generation with multiple sheets
├── duplicate_detector.py  # Duplicate detection logic
├── file_parser.py         # File parsing (CSV, Excel, PDF)
├── templates/             # HTML templates
│   ├── index.html         # Main upload page
│   ├── form.html          # Sample complaint form
│   └── admin.html         # Admin dashboard
├── static/                # CSS and JavaScript
│   ├── style.css
│   └── script.js
├── data/                  # Data storage
│   ├── master_register.xlsx
│   └── uploads/           # Uploaded files
└── requirements.txt
```

## 📊 Excel Output Format

The system generates an Excel file with multiple sheets:

1. **Master_Sheet**: All complaints in one place
2. **UPI_Fraud**: Complaints related to UPI fraud
3. **Bank_Fraud**: Complaints related to bank fraud
4. **Social_Media**: Complaints from social media platforms
5. **Harassment**: Harassment-related complaints
6. **High_Value_Cases**: Cases above threshold amount
7. **Possible_Duplicates**: Flagged duplicate/linked complaints

## 🔒 Compliance & Safety

- ✅ Fully offline operation
- ✅ No cloud storage
- ✅ No API calls to external services
- ✅ Local data storage only
- ✅ No access to real NCRP portal

## 👥 Target Users

Non-technical police officers who need to:
- Organize complaint data efficiently
- Find related complaints quickly
- Track high-value cases
- Identify potential duplicate reports

## 💡 Why This Solution is Useful

1. **Time Saving**: Automatically categorizes complaints instead of manual sorting
2. **Duplicate Awareness**: Helps identify linked complaints that might be the same incident
3. **Multiple Views**: Same data organized in different ways for different investigation needs
4. **Clean Structure**: Standardized format makes data easy to search and filter
5. **Officer-Friendly**: Simple, explainable logic - no black box AI

