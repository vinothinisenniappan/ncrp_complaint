# Setup Guide - NCRP Complaint Organizer

## Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### 2. Installation Steps

#### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- pandas (data processing)
- openpyxl (Excel file handling)
- pdfplumber (PDF parsing)
- Werkzeug (file upload handling)

#### Step 2: Run the Application
```bash
python app.py
```

#### Step 3: Access the Application
Open your web browser and navigate to:
```
http://localhost:5000
```

## Testing the System

### Method 1: Upload Sample CSV File
1. Use the provided `sample_data.csv` file
2. Go to the Upload page
3. Select and upload the CSV file
4. Click "Upload and Process"
5. Download the generated Excel file

### Method 2: Use the Demo Form
1. Click on "Demo Form" in the navigation
2. Fill out the sample complaint form
3. Submit the form
4. Download the generated Excel file

### Method 3: Upload Your Own Files
You can upload:
- **CSV files** with complaint data
- **Excel files** (.xlsx, .xls) with complaint data
- **PDF files** (dummy NCRP format)

## Understanding the Output

### Excel File Structure

The system generates an Excel file (`data/master_register.xlsx`) with multiple sheets:

1. **Master_Sheet**
   - Contains ALL complaints
   - Single source of truth
   - All columns: ID, Date, Name, Mobile, Email, District, Crime Type, Platform, Amount, Status, etc.

2. **Category Sheets** (e.g., UPI_Fraud, Bank_Fraud, Social_Media)
   - Contains complaints filtered by crime type
   - Same complaint appears in master sheet AND relevant category sheet
   - This is NOT duplication - it's multiple views

3. **High_Value_Cases**
   - Cases with amount ≥ ₹50,000
   - Sorted by amount (descending)

4. **Possible_Duplicates**
   - Groups of complaints that might be duplicates
   - Shows match reason (same mobile, same email, same amount, etc.)
   - Officer can review and decide

## File Formats

### CSV Format
Your CSV should have columns like:
- Complaint ID
- Complaint Date
- Complainant Name
- Mobile
- Email
- District
- Crime Type
- Platform
- Amount
- Status

The system will auto-detect column names (case-insensitive).

### Excel Format
Same as CSV, but in Excel format (.xlsx or .xls).

### PDF Format
The system can extract data from PDF files that contain complaint information. The parser looks for:
- Complaint ID / Acknowledgement Number
- Dates
- Names, mobile numbers, emails
- Amounts
- Crime types and platforms

## Troubleshooting

### Issue: "No complaints found in the file"
- Check if your file has the correct format
- Ensure column names match expected fields
- Try with the sample_data.csv file first

### Issue: "Error processing file"
- Check file size (max 16MB)
- Ensure file is not corrupted
- Check file format (CSV, Excel, or PDF)

### Issue: Excel file not downloading
- Ensure at least one file has been uploaded
- Check if `data/master_register.xlsx` exists
- Try uploading a file again

### Issue: Port 5000 already in use
- Change the port in `app.py` (last line)
- Or stop the other application using port 5000

## Data Storage

- **Uploaded files**: Stored in `data/uploads/`
- **Master register**: Stored in `data/master_register.xlsx`
- All data is stored locally (offline)

## Security Notes

- This is a local, offline system
- No data is sent to external servers
- No connection to real NCRP portal
- All processing happens on your machine

## Next Steps

1. Upload your complaint files
2. Review the categorized Excel output
3. Use the duplicate detection to find linked complaints
4. Export and share the Excel file with your team

For questions or issues, refer to the main README.md file.

