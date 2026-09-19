#from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_ollama import ChatOllama
from langchain.tools import tool
from pathlib import Path
import os

agent_model = ChatOllama(
    model="gemma4:cloud",
    validate_model_on_init=True,
    temperature=0,
)

@tool
def csv_agnet_tool(question:str):
    '''
    This tool is to analyze the csv files and provide the answers.
    args:
    question (str): user question that should run on csv file.
    
    '''
    

    agent = create_csv_agent(
            agent_model,
            'document_folder\student_performance_dataset.csv',
            verbose=True,
            #agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            allow_dangerous_code=True
        )
    response=agent.run(question)

    return response
       
    