# query_generator.py

import pandas as pd
import json
import logging
from typing import List, Dict, Any
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate


class QueryGenerator:
    """
    A class to generate relevant queries based on CSV schema and data insights
    """
    
    def __init__(self, llm, logger=None):
        """
        Initialize QueryGenerator with LLM instance
        
        Args:
            llm: The language model instance to use for query generation
            logger: Logger instance (optional)
        """
        self.llm = llm
        self.logger = logger or logging.getLogger(__name__)
        
    def analyze_csv_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze CSV schema and extract relevant information
        
        Args:
            df: Pandas DataFrame to analyze
            
        Returns:
            Dictionary containing schema information
        """
        try:
            schema_info = {
                "columns": list(df.columns),
                "dtypes": df.dtypes.to_dict(),
                "shape": df.shape,
                "numeric_columns": list(df.select_dtypes(include=['number']).columns),
                "categorical_columns": list(df.select_dtypes(include=['object', 'category']).columns),
                "sample_data": df.head(3).to_dict('records'),
                "null_counts": df.isnull().sum().to_dict(),
                "unique_counts": {col: df[col].nunique() for col in df.columns}
            }
            
            # Add basic statistics for numeric columns
            if schema_info["numeric_columns"]:
                schema_info["numeric_stats"] = df[schema_info["numeric_columns"]].describe().to_dict()
                
            return schema_info
            
        except Exception as e:
            self.logger.error(f"Error analyzing CSV schema: {e}")
            raise
    
    def generate_query_suggestions(self, df: pd.DataFrame, max_queries: int = 8) -> List[str]:
        """
        Generate relevant query suggestions based on CSV schema
        
        Args:
            df: Pandas DataFrame to analyze
            max_queries: Maximum number of queries to generate
            
        Returns:
            List of suggested queries
        """
        try:
            # Analyze schema
            schema_info = self.analyze_csv_schema(df)
            
            # Create prompt for query generation
            query_generation_prompt = self._get_query_generation_prompt()
            
            # Setup chain
            output_parser = StrOutputParser()
            chain = query_generation_prompt | self.llm | output_parser
            
            # Generate queries
            response = chain.invoke({
                "schema_info": self._format_schema_for_prompt(schema_info),
                "max_queries": max_queries
            })
            
            # Parse response to extract queries
            queries = self._parse_query_response(response)
            
            self.logger.info(f"Generated {len(queries)} query suggestions")
            return queries[:max_queries]  # Ensure we don't exceed max_queries
            
        except Exception as e:
            self.logger.error(f"Error generating query suggestions: {e}")
            # Return fallback queries if generation fails
            return self._get_fallback_queries(df)
    
    def _get_query_generation_prompt(self) -> PromptTemplate:
        """
        Get the prompt template for query generation
        
        Returns:
            PromptTemplate for generating queries
        """
        prompt_text = """
        You are a data analysis expert. Based on the CSV schema and sample data provided below, generate {max_queries} relevant and insightful queries that would help users explore and understand their data better.

        CSV Schema Information:
        {schema_info}

        Requirements:
        1. Generate practical queries that provide meaningful insights
        2. Include a mix of different query types: descriptive statistics, filtering, grouping, comparisons, trends
        3. Make queries specific to the actual columns and data types present
        4. Ensure queries are suitable for data analysis and visualization
        5. Keep queries concise and user-friendly
        6. Focus on business/analytical insights rather than just basic data operations

        Return ONLY a JSON list of query strings, like this format:
        ["query1", "query2", "query3", ...]

        Generated Queries:
        """
        
        return PromptTemplate.from_template(prompt_text)
    
    def _format_schema_for_prompt(self, schema_info: Dict[str, Any]) -> str:
        """
        Format schema information for the prompt
        
        Args:
            schema_info: Dictionary containing schema information
            
        Returns:
            Formatted string for the prompt
        """
        formatted = f"""
        Columns: {schema_info['columns']}
        Data Types: {schema_info['dtypes']}
        Shape: {schema_info['shape']} (rows, columns)
        Numeric Columns: {schema_info['numeric_columns']}
        Categorical Columns: {schema_info['categorical_columns']}
        
        Sample Data (first 3 rows):
        {schema_info['sample_data']}
        
        Null Counts: {schema_info['null_counts']}
        Unique Value Counts: {schema_info['unique_counts']}
        """
        
        if schema_info.get('numeric_stats'):
            formatted += f"\nNumeric Statistics:\n{schema_info['numeric_stats']}"
            
        return formatted
    
    def _parse_query_response(self, response: str) -> List[str]:
        """
        Parse the LLM response to extract query list
        
        Args:
            response: Raw response from LLM
            
        Returns:
            List of parsed queries
        """
        try:
            # Try to parse as JSON first
            if '[' in response and ']' in response:
                # Extract JSON array from response
                start_idx = response.find('[')
                end_idx = response.rfind(']') + 1
                json_str = response[start_idx:end_idx]
                queries = json.loads(json_str)
                
                if isinstance(queries, list):
                    return [str(q).strip() for q in queries if q.strip()]
            
            # Fallback: try to extract queries line by line
            lines = response.strip().split('\n')
            queries = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith(('```', 'Generated', 'Queries:')):
                    # Remove numbering, bullets, quotes
                    clean_line = line.lstrip('0123456789.- "\'').rstrip('"\'')
                    if clean_line:
                        queries.append(clean_line)
            
            return queries
            
        except Exception as e:
            self.logger.error(f"Error parsing query response: {e}")
            return []
    
    def _get_fallback_queries(self, df: pd.DataFrame) -> List[str]:
        """
        Get fallback queries when generation fails
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            List of basic fallback queries
        """
        fallback = [
            "Show me the first 10 rows of data",
            "What are the basic statistics for numeric columns?",
            "How many rows and columns are in this dataset?"
        ]
        
        # Add column-specific queries if possible
        if len(df.columns) > 0:
            first_col = df.columns[0]
            fallback.append(f"Show unique values in {first_col}")
            
        if len(df.select_dtypes(include=['number']).columns) > 0:
            numeric_col = df.select_dtypes(include=['number']).columns[0]
            fallback.append(f"Create a histogram of {numeric_col}")
            
        return fallback[:6]  # Return max 6 fallback queries
