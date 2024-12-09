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