# constants.py

from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set

class ModelType(str, Enum):
    """Available model types for the application"""
    NONE = "None"
    GPT = "gpt"
    LLAMA = "llama3-8b-8192"
    MIXTRAL = "mixtral-8x7b-32768"

@dataclass
class SecurityConfig:
    """Security-related configuration"""
    SENSITIVE_PATTERNS: List[str] = field(default_factory=lambda: [ 
        # API Keys and Tokens
        "api_key",
        "api-key",
        "apikey",
        "key",
        "token",
        "secret",    
    ])

@dataclass
class FileConfig:
    """File-related configuration"""
    SAMPLE_FILE_PATH: Path = Path("sample/sample.csv")
    ALLOWED_EXTENSIONS: Set[str] = field(default_factory=lambda: {"csv"})
    MAX_FILE_SIZE_MB: int = 10
    SAMPLE_FILE_NAME: str = "sample.csv"

@dataclass
class UIConfig:
    """UI-related configuration"""
    PAGE_TITLE: str = "Conversations with your vulnerability scans"
    SIDEBAR_IMAGE: str = "images/insight.jpg"
    DEFAULT_QUESTIONS: List[str] = field(default_factory=lambda: [
        "How many rows are there?",
        "Display the first 3 record",
        "what are the headers of the file",
        "Display the records related to Cross Side Scripting or XSS?",
        "Show Pie chart by all severity"
    ])

@dataclass
class LogConfig:
    """Logging configuration"""
    LOGGER_NAME: str = "vulnR"
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "vulnerability_scanner.log"

@dataclass
class APIConfig:
    """API-related configuration"""
    OPENAI_API_URL: str = "https://api.openai.com/v1"
    GROQ_API_URL: str = "https://api.groq.com/v1"
    DEFAULT_TIMEOUT: int = 30

@dataclass
class ErrorMessages:
    """Error messages used throughout the application"""
    FILE_UPLOAD_ERROR: str = "Error uploading file. Please try again."
    API_KEY_MISSING: str = "API key is required"
    INVALID_MODEL: str = "Unsupported model type: {model}"
    FILE_LOAD_ERROR: str = "Error loading CSV file: {error}"
    ANALYSIS_ERROR: str = "Error generating analysis: {error}"
    GENERAL_ERROR: str = "An error occurred. Please check your inputs and try again."

@dataclass
class Messages:
    """Success and information messages"""
    WELCOME_MESSAGE: str = "Chat with the reports (CSV or Excel) and get Insights"
    UPLOAD_PROMPT: str = "Please Upload CSV File to continue ..."
    ANALYSIS_COMPLETE: str = "Analysis completed successfully"
    PROCESSING_MESSAGE: str = "Processing your request..."
    REQUIRED_PROMPT: str = "Please provide all mandatory parameters ..."

@dataclass
class AppConfig:
    """Main application configuration container"""
    file: FileConfig = field(default_factory=FileConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    log: LogConfig = field(default_factory=LogConfig)
    api: APIConfig = field(default_factory=APIConfig)
    sec: SecurityConfig = field(default_factory=SecurityConfig)
    error_messages: ErrorMessages = field(default_factory=ErrorMessages)
    messages: Messages = field(default_factory=Messages)
