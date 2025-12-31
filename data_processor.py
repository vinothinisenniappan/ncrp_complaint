"""
Data Processor Module
Handles normalization and categorization of complaint data
"""

from datetime import datetime
import re


class DataProcessor:
    """Process and normalize complaint data"""
    
    def __init__(self):
        self.crime_type_keywords = {
            'UPI_Fraud': ['upi', 'unified payment', 'phonepe', 'google pay', 'paytm', 'bhim'],
            'Bank_Fraud': ['bank', 'account', 'cheque', 'loan', 'credit card', 'debit card'],
            'Social_Media': ['facebook', 'instagram', 'whatsapp', 'telegram', 'social media', 'twitter'],
            'Harassment': ['harassment', 'threat', 'abuse', 'stalking', 'cyberbullying'],
            'Job_Scam': ['job', 'employment', 'work from home', 'recruitment', 'interview'],
            'Online_Shopping': ['amazon', 'flipkart', 'online shopping', 'e-commerce', 'order'],
            'OTP_Fraud': ['otp', 'one time password', 'verification code']
        }
        
        self.platform_keywords = {
            'UPI': ['upi', 'phonepe', 'google pay', 'paytm', 'bhim'],
            'Bank': ['bank', 'account', 'sbi', 'hdfc', 'icici', 'axis'],
            'Card': ['card', 'credit card', 'debit card', 'atm'],
            'Social_Media': ['facebook', 'instagram', 'whatsapp', 'telegram', 'twitter'],
            'OTP': ['otp', 'sms', 'verification'],
            'Email': ['email', 'gmail', 'yahoo', 'outlook']
        }
    
    def normalize_complaint(self, complaint_data):
        """
        Normalize a single complaint to standard format
        """
        normalized = {
            'complaint_id': self._normalize_id(complaint_data.get('complaint_id', '')),
            'complaint_date': self._normalize_date(complaint_data.get('complaint_date', '')),
            'incident_date': self._normalize_date(complaint_data.get('incident_date', '')),
            'complainant_name': self._normalize_text(complaint_data.get('complainant_name', '')),
            'mobile': self._normalize_mobile(complaint_data.get('mobile', '')),
            'email': self._normalize_email(complaint_data.get('email', '')),
            'district': self._normalize_text(complaint_data.get('district', '')),
            'police_station': self._normalize_text(complaint_data.get('police_station', '')),
            'crime_type': self._categorize_crime_type(complaint_data),
            'platform': self._categorize_platform(complaint_data),
            'amount': self._normalize_amount(complaint_data.get('amount', 0)),
            'status': self._normalize_status(complaint_data.get('status', 'Registered')),
            'description': self._normalize_text(complaint_data.get('description', ''))
        }
        
        return normalized
    
    def _normalize_id(self, complaint_id):
        """Normalize complaint ID"""
        if not complaint_id:
            return f"COMP_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return str(complaint_id).strip().upper()
    
    def _normalize_date(self, date_str):
        """Normalize date to YYYY-MM-DD format"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        date_str = str(date_str).strip()
        
        # Try parsing common formats
        formats = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%y', '%d/%m/%y']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except:
                continue
        
        # If parsing fails, return today's date
        return datetime.now().strftime('%Y-%m-%d')
    
    def _normalize_text(self, text):
        """Normalize text fields"""
        if not text:
            return ''
        return str(text).strip().title()
    
    def _normalize_mobile(self, mobile):
        """Normalize mobile number (10 digits)"""
        if not mobile:
            return ''
        
        mobile = re.sub(r'[^\d]', '', str(mobile))
        if len(mobile) == 10:
            return mobile
        elif len(mobile) > 10:
            return mobile[-10:]  # Take last 10 digits
        return mobile
    
    def _normalize_email(self, email):
        """Normalize email"""
        if not email:
            return ''
        return str(email).strip().lower()
    
    def _normalize_amount(self, amount):
        """Normalize amount to float"""
        if not amount:
            return 0.0
        
        try:
            if isinstance(amount, (int, float)):
                return float(amount)
            
            # Remove currency symbols and commas
            amount_str = str(amount).replace('₹', '').replace(',', '').replace(' ', '')
            return float(re.sub(r'[^\d.]', '', amount_str))
        except:
            return 0.0
    
    def _normalize_status(self, status):
        """Normalize status"""
        if not status:
            return 'Registered'
        
        status = str(status).strip().title()
        valid_statuses = ['Registered', 'Under Enquiry', 'FIR Filed', 'Closed', 'Pending']
        
        # Check if status matches any valid status
        for valid in valid_statuses:
            if valid.lower() in status.lower():
                return valid
        
        return status
    
    def _categorize_crime_type(self, complaint_data):
        """Categorize crime type based on keywords"""
        # Check if already categorized
        if complaint_data.get('crime_type'):
            return complaint_data['crime_type']
        
        # Search in description and other text fields
        search_text = ' '.join([
            str(complaint_data.get('description', '')),
            str(complaint_data.get('crime_type', '')),
            str(complaint_data.get('platform', ''))
        ]).lower()
        
        # Match against keywords
        for crime_type, keywords in self.crime_type_keywords.items():
            for keyword in keywords:
                if keyword.lower() in search_text:
                    return crime_type.replace('_', ' ')
        
        return 'Other'
    
    def _categorize_platform(self, complaint_data):
        """Categorize platform based on keywords"""
        # Check if already categorized
        if complaint_data.get('platform'):
            return complaint_data['platform']
        
        # Search in description and other text fields
        search_text = ' '.join([
            str(complaint_data.get('description', '')),
            str(complaint_data.get('platform', '')),
            str(complaint_data.get('crime_type', ''))
        ]).lower()
        
        # Match against keywords
        for platform, keywords in self.platform_keywords.items():
            for keyword in keywords:
                if keyword.lower() in search_text:
                    return platform
        
        return 'Other'
    
    def categorize_complaints(self, complaints):
        """
        Categorize complaints into different groups
        Returns dictionary with category names as keys and lists of complaints as values
        """
        categories = {
            'UPI_Fraud': [],
            'Bank_Fraud': [],
            'Social_Media': [],
            'Harassment': [],
            'Job_Scam': [],
            'Online_Shopping': [],
            'OTP_Fraud': [],
            'Other': []
        }
        
        for complaint in complaints:
            crime_type = complaint.get('crime_type', 'Other')
            category_key = crime_type.replace(' ', '_')
            
            if category_key in categories:
                categories[category_key].append(complaint)
            else:
                categories['Other'].append(complaint)
        
        return categories
    
    def get_high_value_cases(self, complaints, threshold=50000):
        """Get complaints with amount above threshold"""
        return [c for c in complaints if c.get('amount', 0) >= threshold]

