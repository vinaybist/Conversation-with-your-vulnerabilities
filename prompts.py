# prompts.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class SummaryPrompts:
    """Templates for generating various types of summaries"""
    
    
    GENERAL_SUMMARY: str = """
        You are an Security Analyst and CSV file expert. I need a Security Assessment Summary for a recent security evaluation. The assessment should cover the following key areas:

            Overview: Provide a brief summary of the assessment, including the entity as "AI Consulting" conducting it.
            Mentioned Key Findings based on the content

            Suggested actions for mitigating identified vulnerabilities.
            Conclusion: Summarize the overall security posture of the organization and the importance of implementing the recommendations.

            Next Steps: Outline the proposed action plan, including timelines and responsible parties, and recommend a follow-up assessment schedule.

            Contact Information: Provide contact details for further inquiries or follow-up.

            Please ensure the summary is clear, concise, and actionable and do not mention date anywhere. Also do not print duplicate findinds
            Here is the content which you have to the summary of the assessment :
            {content}
        """    
    
    EXECUTIVE_SUMMARY: str = """
    Create an executive summary of the vulnerability assessment:
    1. High-level overview
    2. Critical findings
    3. Key recommendations
    4. Resource implications
    
    Assessment data: {data}
    """
    
    TECHNICAL_SUMMARY: str = """
    Generate a technical summary including:
    1. Detailed vulnerability breakdown
    2. Technical impact analysis
    3. Specific remediation steps
    4. Required technical resources
    
    Technical data: {data}
    """

@dataclass
class ColumnPrompts:
   
    COLUMN_IDENTIFIER: str = """You are an CSV file expert. You have to tell that which column is likely 
    represent the description or summary. Strictly give only the name of it. 
    Here is the CSV file columns : {columns}
    """


class PromptTemplates:
    """Main class to access all prompt templates"""
    
    def __init__(self):
        self.desc_column = ColumnPrompts()
        self.summary = SummaryPrompts()
    
    def get_custom_prompt(self, template: str, **kwargs) -> str:
        """
        Create a custom prompt by formatting the template with provided kwargs
        
        Args:
            template (str): The prompt template to use
            **kwargs: Variables to format the template with
            
        Returns:
            str: Formatted prompt
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {e}")