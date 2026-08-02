import os
import re
from typing import Dict, Any, List

class DocumentClassifier:
    """
    DocumentClassifier analyzes filenames and folder structures of scanned files 
    and groups them into logical corporate/financial categories.
    """
    
    # Regex patterns matching specific document identity categories
    # Order matters: more specific categories (like AUDITOR_REPORT) are checked before broader ones.
    PATTERNS = {
        'ANNUAL_REPORT': [r'annual.*report', r'ar\d{2,4}'],
        'AUDITOR_REPORT': [r'auditor.*report', r'audit.*report'],
        'FINANCIAL_STATEMENTS': [r'financial.*statement', r'balance.*sheet', r'profit.*loss', r'pnl', r'financials'],
        'COMPANY_PROFILE': [r'company.*profile', r'corporate.*profile', r'profile'],
        'IPO_DETAILS': [r'ipo.*details', r'ipo.*config', r'issue.*details'],
        'SHAREHOLDING': [r'shareholder', r'shareholding', r'cap.*table', r'ownership', r'equity'],
        'LITIGATION': [r'litigation', r'lawsuit', r'court', r'dispute'],
        'MATERIAL_CONTRACT': [r'contract', r'agreement', r'mou', r'lease', r'vendor'],
        'GOVERNMENT_APPROVAL': [r'approval', r'certificate', r'license', r'noc', r'sebi', r'roc', r'incorporation'],
        'LEGAL_DOCUMENT': [r'legal', r'notices', r'deed']
    }

    def classify_file(self, file_name: str, relative_path: str) -> str:
        """
        Determines the category of a file by matching its path segments and name against predefined rules.
        """
        name_lower = file_name.lower()
        path_lower = relative_path.lower()
        
        # 1. Inspect relative path folder tags first
        path_parts = path_lower.split('/')
        if 'contracts' in path_parts:
            return 'MATERIAL_CONTRACT'
        if 'approvals' in path_parts or 'certificates' in path_parts:
            return 'GOVERNMENT_APPROVAL'
            
        # 2. Scan regex pattern matches in filename and directory path
        for category, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, name_lower) or re.search(pattern, path_lower):
                    return category
                    
        return 'UNKNOWN'

    def classify_files(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes a list of file metadata items and enriches each with a 'category' tag.
        """
        for file_info in files:
            file_info['category'] = self.classify_file(file_info['name'], file_info['path'])
        return files
