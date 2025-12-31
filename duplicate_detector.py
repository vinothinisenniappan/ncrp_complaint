"""
Duplicate Detector Module
Identifies possible duplicate or linked complaints
"""

from datetime import datetime, timedelta
from difflib import SequenceMatcher


class DuplicateDetector:
    """Detect possible duplicate or linked complaints"""
    
    def __init__(self):
        self.similarity_threshold = 0.8  # 80% similarity for text matching
        self.date_tolerance_days = 7  # Complaints within 7 days are considered
    
    def find_duplicates(self, complaints):
        """
        Find possible duplicate/linked complaints
        Returns list of duplicate groups
        """
        duplicate_groups = []
        processed = set()
        
        for i, complaint1 in enumerate(complaints):
            if i in processed:
                continue
            
            group = [complaint1]
            
            for j, complaint2 in enumerate(complaints[i+1:], start=i+1):
                if j in processed:
                    continue
                
                if self._is_duplicate(complaint1, complaint2):
                    group.append(complaint2)
                    processed.add(j)
            
            if len(group) > 1:
                duplicate_groups.append(group)
                processed.add(i)
        
        return duplicate_groups
    
    def _is_duplicate(self, complaint1, complaint2):
        """
        Check if two complaints are likely duplicates
        Uses multiple matching criteria
        """
        # Exact match on complaint ID
        if (complaint1.get('complaint_id') and complaint2.get('complaint_id') and
            complaint1['complaint_id'] == complaint2['complaint_id']):
            return True
        
        # Same mobile number
        mobile1 = complaint1.get('mobile', '')
        mobile2 = complaint2.get('mobile', '')
        if mobile1 and mobile2 and mobile1 == mobile2:
            # Check if dates are close and amounts are similar
            if self._dates_close(complaint1, complaint2) and self._amounts_similar(complaint1, complaint2):
                return True
        
        # Same email
        email1 = complaint1.get('email', '')
        email2 = complaint2.get('email', '')
        if email1 and email2 and email1 == email2:
            # Check if dates are close and amounts are similar
            if self._dates_close(complaint1, complaint2) and self._amounts_similar(complaint1, complaint2):
                return True
        
        # Similar UPI/bank details (if available in description)
        if self._similar_payment_details(complaint1, complaint2):
            if self._dates_close(complaint1, complaint2) and self._amounts_similar(complaint1, complaint2):
                return True
        
        # Similar names and amounts
        name1 = complaint1.get('complainant_name', '').lower()
        name2 = complaint2.get('complainant_name', '').lower()
        if name1 and name2 and self._text_similarity(name1, name2) > self.similarity_threshold:
            if self._dates_close(complaint1, complaint2) and self._amounts_similar(complaint1, complaint2):
                return True
        
        return False
    
    def _dates_close(self, complaint1, complaint2):
        """Check if complaint dates are within tolerance"""
        try:
            date1_str = complaint1.get('complaint_date', '')
            date2_str = complaint2.get('complaint_date', '')
            
            if not date1_str or not date2_str:
                return False
            
            date1 = datetime.strptime(date1_str, '%Y-%m-%d')
            date2 = datetime.strptime(date2_str, '%Y-%m-%d')
            
            days_diff = abs((date1 - date2).days)
            return days_diff <= self.date_tolerance_days
        except:
            return False
    
    def _amounts_similar(self, complaint1, complaint2):
        """Check if amounts are similar (within 10% or exact match)"""
        amount1 = complaint1.get('amount', 0)
        amount2 = complaint2.get('amount', 0)
        
        if amount1 == 0 or amount2 == 0:
            return False
        
        # Exact match
        if amount1 == amount2:
            return True
        
        # Within 10% difference
        diff = abs(amount1 - amount2)
        avg = (amount1 + amount2) / 2
        if avg > 0:
            percentage_diff = (diff / avg) * 100
            return percentage_diff <= 10
        
        return False
    
    def _similar_payment_details(self, complaint1, complaint2):
        """Check if payment details (UPI ID, account number) are similar"""
        desc1 = str(complaint1.get('description', '')).lower()
        desc2 = str(complaint2.get('description', '')).lower()
        
        # Extract UPI IDs (format: xyz@paytm, etc.)
        import re
        upi_pattern = r'[\w\.-]+@[\w\.-]+'
        
        upi1 = set(re.findall(upi_pattern, desc1))
        upi2 = set(re.findall(upi_pattern, desc2))
        
        if upi1 and upi2 and upi1.intersection(upi2):
            return True
        
        # Extract account numbers (10-16 digits)
        acc_pattern = r'\b\d{10,16}\b'
        acc1 = set(re.findall(acc_pattern, desc1))
        acc2 = set(re.findall(acc_pattern, desc2))
        
        if acc1 and acc2 and acc1.intersection(acc2):
            return True
        
        return False
    
    def _text_similarity(self, text1, text2):
        """Calculate text similarity ratio (0-1)"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def format_duplicate_groups(self, duplicate_groups):
        """
        Format duplicate groups for Excel output
        Returns list of dictionaries with duplicate information
        """
        formatted = []
        
        for group_idx, group in enumerate(duplicate_groups, 1):
            for complaint in group:
                formatted.append({
                    'duplicate_group_id': f"DUPLICATE_GROUP_{group_idx}",
                    'complaint_id': complaint.get('complaint_id', ''),
                    'complaint_date': complaint.get('complaint_date', ''),
                    'complainant_name': complaint.get('complainant_name', ''),
                    'mobile': complaint.get('mobile', ''),
                    'email': complaint.get('email', ''),
                    'amount': complaint.get('amount', 0),
                    'crime_type': complaint.get('crime_type', ''),
                    'platform': complaint.get('platform', ''),
                    'status': complaint.get('status', ''),
                    'match_reason': self._get_match_reason(group, complaint),
                    'group_size': len(group)
                })
        
        return formatted
    
    def _get_match_reason(self, group, complaint):
        """Determine why complaints were matched"""
        reasons = []
        
        # Check for same mobile
        mobiles = [c.get('mobile', '') for c in group if c.get('mobile')]
        if len(set(mobiles)) == 1 and len(mobiles) > 1:
            reasons.append("Same Mobile Number")
        
        # Check for same email
        emails = [c.get('email', '') for c in group if c.get('email')]
        if len(set(emails)) == 1 and len(emails) > 1:
            reasons.append("Same Email")
        
        # Check for same complaint ID
        ids = [c.get('complaint_id', '') for c in group if c.get('complaint_id')]
        if len(set(ids)) == 1 and len(ids) > 1:
            reasons.append("Same Complaint ID")
        
        # Check for similar amounts
        amounts = [c.get('amount', 0) for c in group]
        if len(set(amounts)) == 1:
            reasons.append("Same Amount")
        
        return "; ".join(reasons) if reasons else "Similar Details"

