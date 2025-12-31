"""
File Parser Module
Handles parsing of CSV, Excel, and PDF files to extract complaint data
"""

import pandas as pd
import pdfplumber
from datetime import datetime
import re
import os
from zipfile import ZipFile, BadZipFile


class FileParser:
    """Parse various file formats to extract complaint data"""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls', '.pdf']
    
    def detect_file_type(self, file_path):
        """
        Detect actual file type using magic bytes (file signature)
        Returns: 'pdf', 'xlsx', 'xls', 'csv', or 'unknown'
        """
        try:
            # Read first few bytes to detect file type
            with open(file_path, 'rb') as f:
                header = f.read(8)
            
            # PDF signature: %PDF-
            if header.startswith(b'%PDF-'):
                return 'pdf'
            
            # Excel XLSX signature: PK (ZIP archive)
            if header.startswith(b'PK\x03\x04'):
                # Check if it's actually an Excel file
                try:
                    with ZipFile(file_path, 'r') as z:
                        if '[Content_Types].xml' in z.namelist():
                            # Check for Excel-specific files
                            if any('xl/' in name for name in z.namelist()):
                                return 'xlsx'
                except (BadZipFile, Exception):
                    pass
            
            # Excel XLS signature (old format): D0 CF 11 E0 A1 B1 1A E1
            if header[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
                return 'xls'
            
            # CSV: Check if it's text and has comma-separated values
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    if ',' in first_line or ';' in first_line:
                        return 'csv'
            except:
                pass
            
            return 'unknown'
        except Exception as e:
            raise ValueError(f"Error detecting file type: {str(e)}")
    
    def is_valid_xlsx(self, file_path):
        """
        Validate that the file is a valid Excel XLSX file
        """
        try:
            with ZipFile(file_path, 'r') as z:
                # Check for required Excel structure
                if '[Content_Types].xml' not in z.namelist():
                    return False
                # Check for Excel-specific directories
                if not any('xl/' in name for name in z.namelist()):
                    return False
                return True
        except (BadZipFile, Exception):
            return False
    
    def parse_file(self, file_path):
        """
        Parse a file and return list of complaint dictionaries
        Detects actual file type, not just extension
        """
        # Check if file exists and has content
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError("Uploaded file is empty (0 bytes). Please check the file and try again.")
        
        # Detect actual file type
        actual_type = self.detect_file_type(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Map extensions to expected types
        extension_type_map = {
            '.pdf': 'pdf',
            '.xlsx': 'xlsx',
            '.xls': 'xls',
            '.csv': 'csv'
        }
        
        expected_type = extension_type_map.get(file_ext, 'unknown')
        
        # If we couldn't detect the type but have a valid extension, try using extension
        # (some files might not have clear signatures but still be valid)
        if actual_type == 'unknown' and expected_type != 'unknown':
            actual_type = expected_type
        
        # Warn if extension doesn't match actual detected type
        if actual_type != expected_type and actual_type != 'unknown' and expected_type != 'unknown':
            raise ValueError(
                f"File type mismatch detected! File extension suggests {file_ext}, "
                f"but file content indicates it's actually {actual_type}. "
                f"Please ensure the file extension matches the actual file type. "
                f"(Example: A PDF file should have .pdf extension, not .xlsx)"
            )
        
        # Route to appropriate parser based on actual file type
        if actual_type == 'pdf':
            return self._parse_pdf(file_path)
        elif actual_type == 'xlsx':
            if not self.is_valid_xlsx(file_path):
                raise ValueError(
                    "Invalid or corrupted Excel file. The file may be: "
                    "1) A PDF/CSV renamed as .xlsx, 2) A corrupted download, "
                    "3) Not a valid Excel file. Please upload a valid .xlsx file."
                )
            return self._parse_excel(file_path)
        elif actual_type == 'xls':
            return self._parse_excel(file_path)
        elif actual_type == 'csv':
            return self._parse_csv(file_path)
        else:
            raise ValueError(
                f"Unsupported or unrecognized file type. "
                f"Expected: PDF, Excel (.xlsx, .xls), or CSV. "
                f"File extension: {file_ext}. "
                f"Please ensure you're uploading a valid file of the correct type."
            )
    
    def _parse_csv(self, file_path):
        """Parse CSV file with validation"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("Could not read CSV file. Unsupported encoding.")
            
            # Check if DataFrame is empty
            if df.empty:
                raise ValueError("CSV file is empty or contains no data.")
            
            return self._dataframe_to_complaints(df)
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file appears to be empty or has no readable data.")
        except Exception as e:
            error_msg = str(e)
            if 'BadZipFile' in error_msg or 'Excel' in error_msg:
                raise ValueError(
                    "File appears to be an Excel file, not a CSV. "
                    "Please use .xlsx or .xls extension for Excel files."
                )
            raise ValueError(f"Error parsing CSV file: {error_msg}")
    
    def _parse_excel(self, file_path):
        """Parse Excel file with validation"""
        try:
            # Additional validation before reading
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.xlsx':
                # Validate XLSX before reading
                if not self.is_valid_xlsx(file_path):
                    raise ValueError(
                        "Invalid Excel file. The file may be corrupted or not a valid .xlsx file. "
                        "Please check the file and try again."
                    )
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Check if DataFrame is empty
            if df.empty:
                raise ValueError("Excel file is empty or contains no data.")
            
            return self._dataframe_to_complaints(df)
        except pd.errors.EmptyDataError:
            raise ValueError("Excel file appears to be empty or has no readable data.")
        except Exception as e:
            error_msg = str(e)
            if 'BadZipFile' in error_msg or '[Content_Types].xml' in error_msg:
                raise ValueError(
                    "Invalid Excel file format. The file may be: "
                    "1) A PDF or CSV file renamed as .xlsx, "
                    "2) A corrupted Excel file, "
                    "3) Not a valid Excel file. "
                    "Please upload a valid .xlsx or .xls file."
                )
            raise ValueError(f"Error parsing Excel file: {error_msg}")
    
    def _parse_pdf(self, file_path):
        """Parse PDF file (dummy NCRP format)"""
        complaints = []
        
        try:
            # Validate PDF file
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if not header.startswith(b'%PDF-'):
                    raise ValueError(
                        "Invalid PDF file. The file may be corrupted or not a valid PDF. "
                        "Please ensure you're uploading a valid PDF file."
                    )
            
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) == 0:
                    raise ValueError("PDF file contains no pages.")
                
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        # Extract complaint data from PDF text
                        complaint = self._extract_from_pdf_text(text)
                        if complaint:
                            complaints.append(complaint)
            
            if not complaints:
                raise ValueError(
                    "No complaint data found in PDF. "
                    "Please ensure the PDF contains readable complaint information."
                )
        except pdfplumber.exceptions.PDFSyntaxError:
            raise ValueError(
                "Invalid or corrupted PDF file. The file may be: "
                "1) An Excel or CSV file renamed as .pdf, "
                "2) A corrupted PDF file, "
                "3) Not a valid PDF file. "
                "Please upload a valid PDF file."
            )
        except Exception as e:
            error_msg = str(e)
            if 'BadZipFile' in error_msg or 'Excel' in error_msg or '[Content_Types].xml' in error_msg:
                raise ValueError(
                    "File appears to be an Excel file, not a PDF. "
                    "Please use .xlsx or .xls extension for Excel files, and .pdf for PDF files."
                )
            raise ValueError(f"Error parsing PDF: {error_msg}")
        
        return complaints
    
    def _extract_from_pdf_text(self, text):
        """
        Extract complaint data from PDF text
        This is a simplified parser - can be enhanced based on actual PDF format
        """
        complaint = {}
        
        # Extract Complaint ID / Acknowledgement Number
        id_match = re.search(r'(?:Complaint\s*ID|Acknowledgment|Ack\.?\s*No\.?)[:\s]+([A-Z0-9\-]+)', text, re.IGNORECASE)
        if id_match:
            complaint['complaint_id'] = id_match.group(1).strip()
        else:
            # Generate a temporary ID if not found
            complaint['complaint_id'] = f"TEMP_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Extract dates
        date_patterns = [
            r'(?:Complaint\s*Date|Date\s*of\s*Complaint)[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:Incident\s*Date|Date\s*of\s*Incident)[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    complaint['complaint_date'] = self._parse_date(date_str)
                except:
                    complaint['complaint_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Extract name
        name_match = re.search(r'(?:Name|Complainant\s*Name)[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
        if name_match:
            complaint['complainant_name'] = name_match.group(1).strip()
        
        # Extract mobile
        mobile_match = re.search(r'(?:Mobile|Phone|Contact)[:\s]+(\d{10})', text, re.IGNORECASE)
        if mobile_match:
            complaint['mobile'] = mobile_match.group(1).strip()
        
        # Extract email
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
        if email_match:
            complaint['email'] = email_match.group(1).strip()
        
        # Extract district
        district_match = re.search(r'(?:District)[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
        if district_match:
            complaint['district'] = district_match.group(1).strip()
        
        # Extract amount
        amount_match = re.search(r'(?:Amount|Loss|Lost)[:\s]*₹?\s*(\d+(?:[.,]\d+)?)', text, re.IGNORECASE)
        if amount_match:
            complaint['amount'] = float(amount_match.group(1).replace(',', ''))
        
        # Extract crime type
        crime_types = ['UPI', 'Bank', 'Fraud', 'Harassment', 'Scam', 'Social Media']
        for crime in crime_types:
            if re.search(crime, text, re.IGNORECASE):
                complaint['crime_type'] = crime
                break
        
        # Extract platform
        platforms = ['UPI', 'Bank', 'Card', 'Social Media', 'OTP', 'WhatsApp', 'Facebook']
        for platform in platforms:
            if re.search(platform, text, re.IGNORECASE):
                complaint['platform'] = platform
                break
        
        # Extract status
        status_match = re.search(r'(?:Status)[:\s]+([A-Za-z\s]+)', text, re.IGNORECASE)
        if status_match:
            complaint['status'] = status_match.group(1).strip()
        else:
            complaint['status'] = 'Registered'
        
        return complaint if complaint else None
    
    def _parse_date(self, date_str):
        """Parse various date formats"""
        formats = ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%y', '%d/%m/%y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except:
                continue
        return datetime.now().strftime('%Y-%m-%d')
    
    def _dataframe_to_complaints(self, df):
        """Convert DataFrame to list of complaint dictionaries"""
        complaints = []
        
        # Normalize column names (case-insensitive, handle variations)
        column_mapping = {
            'complaint_id': ['complaint id', 'complaint_id', 'acknowledgment', 'ack no', 'complaint no'],
            'complaint_date': ['complaint date', 'date', 'complaint_date', 'date of complaint'],
            'incident_date': ['incident date', 'incident_date', 'date of incident'],
            'complainant_name': ['name', 'complainant name', 'complainant_name', 'complainant'],
            'mobile': ['mobile', 'phone', 'contact', 'mobile no', 'phone number'],
            'email': ['email', 'e-mail', 'email id'],
            'district': ['district', 'location', 'area'],
            'crime_type': ['crime type', 'crime_type', 'type', 'category'],
            'platform': ['platform', 'medium', 'source'],
            'amount': ['amount', 'loss', 'lost', 'amount lost'],
            'status': ['status', 'current status', 'case status'],
            'police_station': ['police station', 'station', 'ps', 'police_station']
        }
        
        # Create normalized column mapping
        normalized_cols = {}
        for key, variations in column_mapping.items():
            for col in df.columns:
                if col.lower().strip() in [v.lower() for v in variations]:
                    normalized_cols[key] = col
                    break
        
        # Convert each row to a complaint dictionary
        for idx, row in df.iterrows():
            complaint = {}
            for key, col_name in normalized_cols.items():
                if col_name in df.columns and pd.notna(row[col_name]):
                    complaint[key] = str(row[col_name]).strip()
            
            # Generate complaint ID if missing
            if 'complaint_id' not in complaint or not complaint.get('complaint_id'):
                complaint['complaint_id'] = f"COMP_{datetime.now().strftime('%Y%m%d%H%M%S')}_{idx}"
            
            # Parse amount if present
            if 'amount' in complaint:
                try:
                    complaint['amount'] = float(str(complaint['amount']).replace(',', '').replace('₹', '').strip())
                except:
                    complaint['amount'] = 0.0
            
            # Set default values
            if 'status' not in complaint:
                complaint['status'] = 'Registered'
            if 'complaint_date' not in complaint:
                complaint['complaint_date'] = datetime.now().strftime('%Y-%m-%d')
            
            complaints.append(complaint)
        
        return complaints

