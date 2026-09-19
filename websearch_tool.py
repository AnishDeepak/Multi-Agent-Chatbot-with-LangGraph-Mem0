from langchain_community.tools import DuckDuckGoSearchResults

def web_search_tool(question:str):
    '''
    This tool is helpful when user ask questions about general knowledge, current affairs and updated content which requires web search.
    args:
    question (str): The user question, on which the websearch should perform.
    '''
    web_search_tool = DuckDuckGoSearchResults()
    response=web_search_tool.invoke(question)
    return response