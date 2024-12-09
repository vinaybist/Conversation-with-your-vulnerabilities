# main.py

import streamlit as st
import pandas as pd
import logging
from typing import Any
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI
from langchain_groq.chat_models import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
import streamlit_pills as st_pills

from constants import AppConfig, ModelType
from prompts import PromptTemplates
from utils import Utils

class VulnerabilityScanner:
    def __init__(self):
        self.config = AppConfig()
        self.logger = logging.getLogger(self.config.log.LOGGER_NAME)
        self.setup_logging()
        self.llm = None
        self.df = None
        self.prompts = PromptTemplates()
        
    def setup_logging(self):
        """Initialize logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.log.LOG_LEVEL),
            format=self.config.log.LOG_FORMAT,
            filename=self.config.log.LOG_FILE
        )
    
    def initialize_llm(self, model_type: str, api_key: str) -> Any:
        """Initialize the appropriate LLM based on model selection"""
        if not api_key:
            raise ValueError(self.config.error_messages.API_KEY_MISSING)
            
        if model_type == ModelType.GPT:
            return OpenAI(openai_api_key=api_key)
        elif model_type in [ModelType.LLAMA, ModelType.MIXTRAL]:
            return ChatGroq(
                model=model_type,
                api_key=api_key,
                timeout=self.config.api.DEFAULT_TIMEOUT
            )
        else:
            raise ValueError(
                self.config.error_messages.INVALID_MODEL.format(model=model_type)
            )
    
    def load_data(self, uploaded_file) -> pd.DataFrame:
        """Load and validate the uploaded CSV file"""
        try:
            #self.validate_file(uploaded_file)
            return pd.read_csv(uploaded_file)
        except Exception as e:
            self.logger.error(f"Error loading CSV file: {e}")
            raise ValueError(
                self.config.error_messages.FILE_LOAD_ERROR.format(error=str(e))
            )
    
    def generate_summary(self, df: pd.DataFrame) -> str:
        """Generate a security assessment summary"""
        try:
            # Create prompts
            column_prompt = PromptTemplate.from_template(
                self.prompts.desc_column.COLUMN_IDENTIFIER
            )
            summary_prompt = PromptTemplate.from_template(
                self.prompts.summary.GENERAL_SUMMARY
            )
            
            # Setup chain
            output_parser = StrOutputParser()
            
            # Get description column
            column_chain = column_prompt | self.llm | output_parser
            description_column = column_chain.invoke({"columns": str(df.columns)})
            description_column = Utils.clean_text(description_column)
            print("description_column == ",description_column)
            # Generate content
            content = ' '.join(map(str, df[description_column].values.tolist()))
            
            # Generate summary
            summary_chain = summary_prompt | self.llm | output_parser
            return summary_chain.invoke({"content": content})
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            raise ValueError(
                self.config.error_messages.ANALYSIS_ERROR.format(error=str(e))
            )

    def generate_technical_analysis(self, df: pd.DataFrame) -> str:
        """Generate a technical analysis of vulnerabilities"""
        try:
            prompt = PromptTemplate.from_template(
                self.prompts.summary.TECHNICAL_SUMMARY
            )
            chain = prompt | self.llm | StrOutputParser()
            return chain.invoke({"data": df.to_json()})
        except Exception as e:
            self.logger.error(f"Error generating technical analysis: {e}")
            raise ValueError(
                self.config.error_messages.ANALYSIS_ERROR.format(error=str(e))
            )

    def render_ui(self):
        """Render the Streamlit UI"""
        st.set_page_config(layout="wide")
        st.title(self.config.ui.PAGE_TITLE)
        
        # Sidebar
        st.sidebar.image(
            self.config.ui.SIDEBAR_IMAGE,
            use_column_width=True
        )
        model = st.sidebar.selectbox(
            "Step1: Choose a model",
            [model.value for model in ModelType]
        )
        api_key = st.sidebar.text_input(
            "Step2: Input your API-KEY", 
            value="", 
            type="password"
        )
        uploaded_file = st.sidebar.file_uploader("Step3: Upload csv file", type=self.config.file.ALLOWED_EXTENSIONS)
        print(uploaded_file)
        # Main layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(self.config.messages.WELCOME_MESSAGE)
            
            if all([uploaded_file, api_key, model != ModelType.NONE]):
                try:
                    self.llm = self.initialize_llm(model, api_key)
                    self.df = self.load_data(uploaded_file)
                    
                    # Interactive elements
                    question_selected = st_pills.pills(
                        "Quick options to try..",
                        self.config.ui.DEFAULT_QUESTIONS,
                        [""] * len(self.config.ui.DEFAULT_QUESTIONS)
                    )
                    
                    query_text = st.text_input(
                        placeholder="Query to the File for continue ...",
                        value=question_selected,
                        label="Place Your Queries"
                    )
                    
                    col1a, col1b = st.columns(2)
                    with col1a:
                        summary_button = st.button(
                            "Summary",
                            type="secondary",
                            use_container_width=True
                        )
                    with col1b:
                        technical_button = st.button(
                            "Technical Analysis",
                            type="secondary",
                            use_container_width=True
                        )
                    
                    # Handle interactions
                    if summary_button:
                        with st.spinner(self.config.messages.PROCESSING_MESSAGE):
                            summary = self.generate_summary(self.df)
                            message = st.chat_message("assistant")
                            message.write(summary)
                            st.success(self.config.messages.ANALYSIS_COMPLETE)
                            
                    elif technical_button:
                        with st.spinner(self.config.messages.PROCESSING_MESSAGE):
                            analysis = self.generate_technical_analysis(self.df)
                            message = st.chat_message("assistant")
                            message.write(analysis)
                            st.success(self.config.messages.ANALYSIS_COMPLETE)
                            
                    elif query_text:
                        with st.spinner(self.config.messages.PROCESSING_MESSAGE):
                            dfai = SmartDataframe(self.df, config={"llm": self.llm})
                            response = dfai.chat(query_text)
                            message = st.chat_message("assistant")
                            message.write(response)
                            
                            if isinstance(response, str) and ".png" in response:
                                st.image(response)
                            
                except Exception as e:
                    self.logger.error(f"Application error: {e}")
                    st.error(self.config.error_messages.GENERAL_ERROR)
            else:
                st.warning(self.config.messages.UPLOAD_PROMPT)

def main():
    app = VulnerabilityScanner()
    app.render_ui()

if __name__ == "__main__":
    main()