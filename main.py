# main.py

import streamlit as st
import pandas as pd
import logging
from typing import Any
from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI
from langchain_groq.chat_models import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
import streamlit_pills as st_pills

from constants import AppConfig, ModelType
from utils import Utils
from prompts import PromptTemplates


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
        try:
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
        
        except Exception as e:
            # Ensure we're not logging the API key in error messages
            error_message = str(e)
            if api_key in error_message:
                error_message = error_message.replace(api_key, "[REDACTED]")
            self.logger.error(f"Error initializing LLM: {error_message}")
            raise   
            
    def router(self, user_query, file):
        try:
            # Get prompts
            decision_prompt = PromptTemplate.from_template(
                self.prompts.routing.ROUTING_DECISION_PROMPT3
            )
            
            # Setup chain
            output_parser = StrOutputParser()
            
            # Get routing decision column
            simple_chain = decision_prompt | self.llm | output_parser
            decision_factor = simple_chain.invoke({"user_input": user_query, "file": file})
            self.logger.info("decision_factor == ",decision_factor)

            return decision_factor
            
        except Exception as e:
            self.logger.error(f"Error getting routing : {e}")
            raise ValueError(
                self.config.error_messages.ANALYSIS_ERROR.format(error=str(e))
            )

    def get_pandasai_response(self, df, llm, query_text):
        dfai = SmartDataframe(df, config={"llm": llm})
        response = dfai.chat(query_text)
        return response

    def general_response(self, query_text):
        """For any other general query LLM response """
        try:
            # Get prompts
            system_prompt = ChatPromptTemplate.from_template(
                self.prompts.system.SYSTEM_PROMPT
            )
            
            # Generate response
            response_chain = system_prompt | self.llm | StrOutputParser()
            
            res = response_chain.invoke({"user_input": query_text})
            return res
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            raise ValueError(
                self.config.error_messages.ANALYSIS_ERROR.format(error=str(e))
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
            # Get prompts
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
            self.logger.info("description_column == ",description_column)
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

    # def generate_technical_analysis(self, df: pd.DataFrame) -> str:
        # """Generate a technical analysis of vulnerabilities"""
        # try:
            # prompt = PromptTemplate.from_template(
                # self.prompts.summary.TECHNICAL_SUMMARY
            # )
            # chain = prompt | self.llm | StrOutputParser()
            # return chain.invoke({"data": df.to_json()})
        # except Exception as e:
            # self.logger.error(f"Error generating technical analysis: {e}")
            # raise ValueError(
                # self.config.error_messages.ANALYSIS_ERROR.format(error=str(e))
            # )

    def render_ui(self):
        """Render the Streamlit UI"""
        st.set_page_config(layout="wide")
        st.title(self.config.ui.PAGE_TITLE)

        # Initialize session state for model and API key if not exists
        if 'model_selected' not in st.session_state:
            st.session_state.model_selected = ModelType.NONE
        if 'api_key_value' not in st.session_state:
            st.session_state.api_key_value = ""
        if 'pill_index' not in st.session_state:
            st.session_state.pill_index = None    

        # Sidebar
        st.sidebar.image(
            self.config.ui.SIDEBAR_IMAGE,
            use_column_width=True
        )
        model = st.sidebar.selectbox(
            "Step1: Choose a model",
            [model.value for model in ModelType],
        index=[m.value for m in ModelType].index(st.session_state.model_selected)                                                           
        )
        api_key = st.sidebar.text_input(
            "Step2: Input your API-KEY", 
            value=st.session_state.api_key_value, 
            type="password"
        )
        uploaded_file = st.sidebar.file_uploader(
            "Step3: Upload csv file", 
            type=self.config.file.ALLOWED_EXTENSIONS
        )

        col_sample1, col_sample2 = st.sidebar.columns(2)
        with col_sample1:
            if st.button("Demo Sample"):
                try:
                    sample_data = pd.read_csv(self.config.file.SAMPLE_FILE_PATH)
                    st.session_state.df = sample_data
                    st.session_state.using_sample = True
                    # Set model and API key values
                    st.session_state.model_selected = ModelType.LLAMA
                    st.session_state.api_key_value = "**************************"
                    # # Force a rerun to update the UI
                    st.rerun()                    
                except Exception as e:
                    self.logger.error(f"Error loading sample file: {e}")
                    st.error("Error loading sample file")

        with col_sample2:
            with open(self.config.file.SAMPLE_FILE_PATH, "r") as csvFileObj:
                st.download_button(
                    label="📥Sample CSV",
                    data=csvFileObj,
                    file_name=self.config.file.SAMPLE_FILE_NAME,
                    mime="text/csv",
                )

        # Main layout
        col1, col2 = st.columns([0.95, 0.05])
        
        with col1:
            st.markdown(self.config.messages.WELCOME_MESSAGE)
            
            #if all([uploaded_file, api_key, model != ModelType.NONE]):
            if (uploaded_file or (st.session_state.get('using_sample', True))) and api_key and model != ModelType.NONE:
                try:                    
                    self.llm = self.initialize_llm(model, api_key)
                    #self.df = self.load_data(uploaded_file)
                    # Load data from either source
                    if uploaded_file:
                        self.df = self.load_data(uploaded_file)
                        st.session_state.using_sample = False
                    else:
                        self.df = st.session_state.df        

                    # Interactive elements
                    question_selected = st_pills.pills(
                        "Quick options to try..",
                        self.config.ui.DEFAULT_QUESTIONS,
                        [""] * len(self.config.ui.DEFAULT_QUESTIONS),
                        index=st.session_state.pill_index
                    )
                    query_container = st.container()

                    with query_container:
                        st.write("**Place Your Queries**")  # Header
                        query_cols = st.columns([0.85, 0.15])
                        
                        with query_cols[0]:
                            query_text = st.text_input(
                                label="Place Your Queries",
                                placeholder="Query to the File for continue ...",
                                value=question_selected,
                                label_visibility="collapsed" 
                            )
                        
                        with query_cols[1]:
                            if st.button("Submit", type="secondary", use_container_width=True):
                                # Reset pill selection when Submit is clicked
                                st.session_state.pill_index = None
                                st.rerun()
                    
                    #col1a, col1b = st.columns(2)
                    #with col1a:
                    summary_button = st.button(
                        "Quick Summary",
                        type="secondary",
                        use_container_width=True
                    )
                    # with col1b:
                        # technical_button = st.button(
                            # "Technical Analysis",
                            # type="secondary",
                            # use_container_width=True
                        # )
                    
                    # Handle interactions
                    if summary_button:
                        with st.spinner(self.config.messages.PROCESSING_MESSAGE):
                            summary = self.generate_summary(self.df)
                            message = st.chat_message("assistant")
                            message.write(summary)
                            st.success(self.config.messages.ANALYSIS_COMPLETE)
                            
                    # elif technical_button:
                        # with st.spinner(self.config.messages.PROCESSING_MESSAGE):
                            # analysis = self.generate_technical_analysis(self.df)
                            # message = st.chat_message("assistant")
                            # message.write(analysis)
                            # st.success(self.config.messages.ANALYSIS_COMPLETE)
                            
                    elif query_text:
                        
                        with st.spinner(self.config.messages.PROCESSING_MESSAGE):
                            #get routing info
                            route_text = self.router(query_text,uploaded_file)
                            self.logger.info("route_text ========> ",route_text)
                            #route = json.loads(route_text)["route"]
                            route = str(route_text)
                            if "general" in route:
                                self.logger.info("INSIDE GENERAL ROUTE............\n")
                                # call normal llm with system prompt of VulnR expert
                                response = self.general_response(query_text)
                                message = st.chat_message("assistant")
                                message.write(response)
                            else:
                                self.logger.info("INSIDE PANDASAI ROUTE............\n")
                                response = self.get_pandasai_response(self.df, self.llm, query_text)
                                # dfai = SmartDataframe(self.df, config={"llm": self.llm})
                                # response = dfai.chat(query_text)
                                message = st.chat_message("assistant")
                                message.write(response)
                                
                                # hack to show images on UI
                                if isinstance(response, str) and ".png" in response:
                                    st.image(response)

                except Exception as e:
                    self.logger.error(f"Application error: {e}")
                    st.error(e)
            else:
                st.warning(self.config.messages.REQUIRED_PROMPT)

        with col2:
            pass


def render_agentic_UI():
    pass


def main():
    app = VulnerabilityScanner()
    app.render_ui()

if __name__ == "__main__":
    main()