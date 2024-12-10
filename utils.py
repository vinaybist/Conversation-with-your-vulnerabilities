# utils.py

from typing import Any, Dict, Union, List
import logging
from datetime import datetime

class Utils:
    """Utility class containing helper methods for the application"""


    @staticmethod
    def clean_text(text: str) -> str:
            """
            Clean text by handling special characters and newlines.
            
            Args:
                text (str): Input text to clean
                
            Returns:
                str: Cleaned text
            """
            if not isinstance(text, str):
                return text
                
            # Replace common special characters with their meaningful equivalents
            replacements = {
                '\n': ' ',          # newline to space
                '\r': ' ',          # carriage return to space
                '\t': ' ',          # tab to space
                '\\n': ' ',         # literal \n to space
                '\\r': ' ',         # literal \r to space
                '\\t': ' ',         # literal \t to space
                '\xa0': ' ',        # non-breaking space to space
                '\u2019': "'",      # smart quote to regular quote
                '\u2018': "'",      # smart quote to regular quote
                '\u201c': '"',      # smart quote to regular quote
                '\u201d': '"',      # smart quote to regular quote
            }
            
            for old, new in replacements.items():
                text = text.replace(old, new)
            
            text = ' '.join(text.split())
            
            return text.strip()    
            
    @staticmethod
    def sanitize_log_message(message: str, sensitive_data: Union[str, List[str]]) -> str:
        """
        Sanitize log messages by removing sensitive data
        
        Args:
            message (str): Message to sanitize
            sensitive_data (str or list): Data to redact
            
        Returns:
            str: Sanitized message
        """
        if isinstance(sensitive_data, str):
            sensitive_data = [sensitive_data]
            
        sanitized_message = message
        for data in sensitive_data:
            if data and data in sanitized_message:
                sanitized_message = sanitized_message.replace(data, "[REDACTED]")
                
        return sanitized_message            