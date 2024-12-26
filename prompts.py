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
class RoutePrompts:
    ROUTING_DECISION_PROMPT = """
You are an expert in judging routing based on user queries. 
You will decide the appropriate route for each user query. 

Return your responses in the following format:
{{
    "route": "route_name" 
}}

The route_name can only be one of the following:
- "general": For greetings, conversational queries, and questions unrelated to the uploaded CSV file or data analysis.
- "pandasaiAgent": For any questions related to data analysis, visualization, or the contents of the uploaded file (even if the word "file" is not explicitly mentioned).

Guidelines for route selection:
1. If the query refers to the data, its contents (e.g., rows, columns, or specific information within the file), or requires any computation or analysis, choose "pandasaiAgent".
2. If the query does not pertain to the data or analysis, choose "general".

The uploaded file is a CSV containing vulnerability-related records.

Explain your reasoning for choosing the route after selecting the route.

Here is the user query: {user_input}
Here is the uploaded CSV file: {file}
"""

    ROUTING_DECISION_PROMPT2 = """
You are an expert in determining the appropriate routing for user queries. 
Your task is to decide the route based on the query type.

Respond in the following format:
{{
    "route": "route_name"
}}

The route_name can only be one of:
- "general": For greetings, conversational queries, or those unrelated to the uploaded CSV file or data analysis.
- "pandasaiAgent": For queries requiring data analysis, visualization, or those referring to the contents or structure of the uploaded CSV file (e.g., rows, columns, or specific records).

Guidelines:
1. If the query mentions terms like "rows," "columns," "data," or any other dataset-specific terminology, route to "pandasaiAgent."
2. Even if the query seems straightforward (e.g., "How many rows are there?"), it should be treated as a data-related query if it pertains to the uploaded file.
3. Reserve "general" for completely unrelated questions, such as greetings or casual chat, which do not imply interaction with the data.

The uploaded file is a CSV containing vulnerability-related records.

Explain your reasoning for choosing the route.

Here is the user query: {user_input}
Here is the uploaded CSV file: {file}
"""

    ROUTING_DECISION_PROMPT3 = """
You are an expert in determining the appropriate routing for user queries. 
Your task is to decide the route based on the query type.

Respond in the following format:
{{
    "route": "route_name"
}}

The route_name can only be one of:
- "general": For greetings, conversational queries, or those unrelated to the uploaded CSV file or any data-related operations.
- "pandasaiAgent": For queries requiring data analysis, visualization, filtering, or accessing the contents of the uploaded CSV file (even if the query does not explicitly mention the file).

Guidelines:
1. Route to "pandasaiAgent" if the query:
   - Even if the query does not explicitly mention the "file" word
   - How many rows or columns?
   - Refers to the structure like displaying or counting rows, columns etc in a file.
   - Requests specific records, filtering, counting or querying based on conditions (e.g., "Display records related to X").
   - Implies interaction with or analysis of the dataset in any form.
2. Route to "general" for:
   - Greetings, casual chat, or questions entirely unrelated to the uploaded file.
   - Queries about topics or information outside the scope of data-related operations.

The uploaded file is a CSV containing vulnerability-related records.

Explain your reasoning for choosing the route.

Here is the user query: {user_input}
Here is the uploaded CSV file: {file}
"""


@dataclass
class SystemPrompts:
    """Templates for generating various types of summaries"""
    SYSTEM_PROMPT: str = """You are a Infomation Security Analyst and can give insights on the vulnerability scans data given to you. Try to guide user about your skill that you can give insight about any uploaded scans. Additionally, mention that if user already uploaded the file then he can ask or chat about it. 
    Here is the user query : {user_input} 
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
        self.routing = RoutePrompts()
        self.system = SystemPrompts()
    
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
        