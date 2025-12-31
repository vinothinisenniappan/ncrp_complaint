# System Architecture - NCRP Complaint Organizer

## Overview

This document explains how the NCRP Complaint Organizer system works internally.

## System Components

### 1. File Parser (`file_parser.py`)
**Purpose**: Extract complaint data from various file formats

**Functions**:
- `parse_file()`: Main entry point - determines file type and routes to appropriate parser
- `_parse_csv()`: Parses CSV files using pandas
- `_parse_excel()`: Parses Excel files using pandas
- `_parse_pdf()`: Extracts text from PDF and parses complaint data using regex patterns
- `_extract_from_pdf_text()`: Uses regex to find complaint fields in PDF text
- `_dataframe_to_complaints()`: Converts pandas DataFrame to list of dictionaries

**Key Features**:
- Auto-detects column names (case-insensitive)
- Handles various date formats
- Generates complaint IDs if missing
- Normalizes mobile numbers to 10 digits

### 2. Data Processor (`data_processor.py`)
**Purpose**: Normalize and categorize complaint data

**Functions**:
- `normalize_complaint()`: Converts raw complaint data to standard format
- `categorize_complaints()`: Groups complaints by crime type
- `get_high_value_cases()`: Filters complaints above threshold amount

**Normalization Rules**:
- Dates → YYYY-MM-DD format
- Mobile → 10 digits only
- Email → lowercase
- Amount → float (removes currency symbols)
- Text → Title Case
- Status → Standard values (Registered, Under Enquiry, FIR Filed, Closed, Pending)

**Categorization**:
- Uses keyword matching to determine crime type
- Categories: UPI_Fraud, Bank_Fraud, Social_Media, Harassment, Job_Scam, Online_Shopping, OTP_Fraud, Other

### 3. Duplicate Detector (`duplicate_detector.py`)
**Purpose**: Identify possible duplicate or linked complaints

**Matching Criteria**:
1. **Exact ID Match**: Same complaint ID
2. **Same Mobile + Similar Date + Similar Amount**: Within 7 days, within 10% amount difference
3. **Same Email + Similar Date + Similar Amount**: Same as above
4. **Similar Payment Details**: Same UPI ID or account number in description
5. **Similar Name + Similar Date + Similar Amount**: Name similarity > 80%

**Output**:
- Groups of complaints flagged as possible duplicates
- Match reason for each group
- Group size (number of linked complaints)

**Important**: Duplicates are FLAGGED, not deleted. Officer reviews and decides.

### 4. Excel Generator (`excel_generator.py`)
**Purpose**: Create formatted Excel files with multiple sheets

**Sheets Generated**:
1. **Master_Sheet**: All complaints
2. **Category Sheets**: One per crime type (if complaints exist)
3. **High_Value_Cases**: Complaints ≥ ₹50,000
4. **Possible_Duplicates**: Flagged duplicate groups

**Formatting**:
- Header row: Blue background, white text, bold
- Borders on all cells
- Auto-adjusted column widths
- Frozen header row
- Professional appearance

**Data Flow**:
- Loads existing master register (if exists)
- Appends new complaints (checks for duplicates by ID)
- Generates all sheets
- Applies formatting

### 5. Flask Application (`app.py`)
**Purpose**: Web interface and API endpoints

**Routes**:
- `/`: Main upload page
- `/form`: Sample complaint form (demo)
- `/admin`: Dashboard with statistics
- `/upload`: File upload handler (POST)
- `/submit_form`: Form submission handler (POST)
- `/download`: Download Excel file
- `/api/stats`: JSON API for statistics

**Key Functions**:
- `load_master_register()`: Loads existing Excel file into memory
- File validation and security (secure_filename, allowed extensions)
- Flash messages for user feedback
- Error handling

## Data Flow

```
1. User uploads file OR submits form
   ↓
2. File Parser extracts raw complaint data
   ↓
3. Data Processor normalizes each complaint
   ↓
4. System loads existing master register
   ↓
5. New complaints added (duplicate ID check)
   ↓
6. Data Processor categorizes all complaints
   ↓
7. Duplicate Detector finds possible duplicates
   ↓
8. High-value cases identified
   ↓
9. Excel Generator creates formatted Excel file
   ↓
10. User downloads Excel file
```

## Key Design Decisions

### 1. Why Multiple Sheets?
- **Master Sheet**: Complete view, single source of truth
- **Category Sheets**: Quick access by crime type (officer-friendly)
- **High Value**: Priority cases
- **Duplicates**: Investigation aid

Same complaint appears in multiple sheets - this is intentional (multiple views, not duplication).

### 2. Why Assisted Duplicate Detection?
- Automatic deletion is dangerous (might delete legitimate separate complaints)
- Officer judgment is essential
- System FLAGS possible duplicates, officer DECIDES

### 3. Why Local Storage?
- Compliance: No cloud, no external APIs
- Security: Data stays on local machine
- Offline: Works without internet
- Demo: Safe for demonstration

### 4. Why Simple Logic (No AI)?
- Explainable: Officer can understand why complaint is categorized
- Trustworthy: No black box decisions
- Maintainable: Easy to modify rules
- Appropriate: Hackathon-level project

## File Structure

```
NCRP_Complaint/
├── app.py                 # Flask application (main entry point)
├── file_parser.py          # File parsing logic
├── data_processor.py       # Data normalization & categorization
├── duplicate_detector.py   # Duplicate detection logic
├── excel_generator.py      # Excel file generation
├── requirements.txt        # Python dependencies
├── README.md              # User documentation
├── SETUP_GUIDE.md         # Setup instructions
├── SYSTEM_ARCHITECTURE.md  # This file
├── sample_data.csv        # Sample data for testing
├── templates/             # HTML templates
│   ├── index.html         # Upload page
│   ├── form.html          # Complaint form
│   └── admin.html         # Dashboard
├── static/                # CSS and JavaScript
│   └── style.css
└── data/                  # Data storage
    ├── master_register.xlsx
    └── uploads/           # Uploaded files
```

## Extensibility

### Adding New Crime Types
Edit `data_processor.py`:
- Add to `crime_type_keywords` dictionary
- Add category to `categorize_complaints()` function

### Changing Duplicate Detection Rules
Edit `duplicate_detector.py`:
- Modify `_is_duplicate()` function
- Adjust `similarity_threshold` or `date_tolerance_days`

### Adding New File Formats
Edit `file_parser.py`:
- Add format to `supported_formats`
- Add new `_parse_*()` method

### Modifying Excel Output
Edit `excel_generator.py`:
- Modify `_write_*_sheet()` methods
- Adjust column order or formatting

## Performance Considerations

- **File Size**: Max 16MB upload limit
- **Processing**: Sequential processing (suitable for demo)
- **Memory**: All complaints loaded into memory (fine for local use)
- **Excel**: OpenPyXL handles large files efficiently

## Security Considerations

- **File Upload**: Validates file extensions, uses secure_filename
- **No External APIs**: Fully offline
- **Local Storage**: All data on local machine
- **No Authentication**: Demo system (add if needed for production)

## Future Enhancements (Not in Current Scope)

- Database backend (SQLite/PostgreSQL)
- User authentication
- Advanced search/filtering
- Export to other formats
- Real-time updates
- Multi-user support
- Audit logging

