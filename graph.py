
from typing_extensions import TypedDict
from langgraph.graph import MessagesState, START, END,StateGraph
from langgraph.types import Command
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_ollama import ChatOllama
from rag_retreiver_tool import retriever_tool
from ingest_documents import DocumentIngestion
from websearch_tool import web_search_tool
from csv_agent import csv_agnet_tool
#from guardrail import guardrail_node
from langgraph.checkpoint.memory import InMemorySaver 
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3 

from typing import Literal, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage,SystemMessage,AIMessage
from langgraph.graph.message import add_messages

#checkpointer=InMemorySaver()

agent_model = ChatOllama(
    model="gemma4:cloud",
    validate_model_on_init=True,
    temperature=0,
)


ingestion = DocumentIngestion(
    folder_path="./documents",
    
)


def build_graph(checkpointer):

    class GraphState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]
        guardrail_decision: str
        guardrail_reason: str
        worker_called: str

    class GuardrailResult(TypedDict):
        decision: Literal["ALLOW", "BLOCK"]
        reason: str

    def guardrail_node(state: GraphState):
        prompt='''
        You are a strict input guardrail for an AI assistant.
        Your job is to determine whether the user's request is allowed to proceed.
        Return ONLY valid JSON in exactly this format:
        {{"decision":"ALLOW","reason":"<short reason>"}}
        or
        {{"decision":"BLOCK","reason":"<short reason>"}}
        Do not provide any additional text.

        ========================
        BLOCK THE REQUEST IF:
        ========================

        1. Harmful, illegal, or dangerous requests
        - Instructions for committing crimes or illegal activities
        - Creating weapons, explosives, harmful chemicals, or dangerous devices
        - Hacking, malware, credential theft, phishing, or unauthorized access
        - Bypassing security systems or authentication
        - Instructions intended to cause physical harm
        - Fraud, scams, or identity theft

        2. Sexual or explicit content
        - Pornographic or sexually explicit requests
        - Sexual content involving minors
        - Requests for explicit sexual instructions

        3. Hate, harassment, insulting or abusive content
        - Requests promoting hatred or violence against protected groups
        - Severe harassment or targeted abuse
        - Insulting a person, religion, country,etc..

        4. Self-harm
        - Instructions for suicide or self-harm
        - Methods, dosages, or instructions intended to cause self-injury

        ========================
        BLOCK TECHNICAL REQUESTS IF:
        ========================

        5. Programming / coding tasks
        Do NOT execute or solve programming tasks.

        Block requests such as:
        - "execute Python code"
        - "execute Java code"
        - "Debug this code"
        - "execute a SQL query"
        - "Run an API"
        - "execute JavaScript"
        - "Generate a shell script"
        - "execute a regex"


        6. Command execution
        Do NOT act as a terminal, shell, operating system, or command executor.

        Block requests such as:
        - "Run this Python command"
        - "Execute this Linux command"
        - "Run rm -rf"
        - "Execute this SQL command"
        - "Open the terminal and run..."
        - "Install this package"
        - "Run pip install..."
        - "Run this Docker command"
        - "Execute this script"

        7. Calculator / mathematical computation
        Do NOT act as a calculator. But remember user can ask question and calculations on csv data.

        

        8. Code execution or file manipulation
        Block requests asking the assistant to:
        - Execute code
        - Execute scripts
        - Modify or delete files through commands
        - Access a user's computer
        - Run programs
        - Execute database commands

        ========================
        ALLOW:
        ========================

        Allow normal informational and conversational requests such as:
        - General knowledge questions
        - Questions about concepts
        - Explanations of AI, RAG, LangChain, AWS, etc.
        - Questions about documents or information available in the knowledge base
        - Questions requiring web research
        - Questions about company/profile information
        - Normal business questions
        - Summarization
        - General recommendations
        - Natural-language explanations
        - Questions related to programming, and sample code generation

        Important:
        A question ABOUT programming is allowed if the user is asking for a conceptual explanation rather than asking to  execute code.

        Examples:
        "Explain what LangGraph is" → ALLOW
        "What is an API?" → ALLOW
        "How does RAG work?" → ALLOW
        "Explain Python decorators" → ALLOW
        "Give me a sample code for <topic>" -> ALLOW
    

        But:
        "Execute Python code for RAG" → BLOCK
        "Debug and run my Python code" → BLOCK
        "Give me a funny quote on my fatty coleaguge" -> BLOCK

        ========================
        DECISION RULE:
        ========================

        If the request clearly falls into any BLOCK category, return BLOCK.

        If the request is ambiguous but could reasonably be interpreted as a programming, command-execution, calculator, harmful, illegal, or security-related request, return BLOCK.

        Otherwise return ALLOW.

        Return ONLY JSON.   

        '''

        messages = [
            SystemMessage(content=prompt),
            *state["messages"]
        ]

        response = agent_model.with_structured_output(
            GuardrailResult
        ).invoke(messages)

        return {
            "guardrail_decision": response["decision"],
            "guardrail_reason": response["reason"]
        }
        

    #vectorstore = ingestion.run()

    member_agents = ["web_search_agent", "rag_agent", "csv_agent"]

    task_options = member_agents + ["FINISH"]



    # Create system prompt for supervisor
    system_prompt = f'''
        - You are a supervisor AI agent designed to provide the response for user queries using the following worker agents: workers: {member_agents}.
        - Given a user query, select the appropriate worker to get the answer for user query.
        - Once you receive the answer from the worker aget, respond with "FINISH" to complete the flow.
        - So your options for this task should be from the list: {task_options}.
        - Strikly call any worker one time only, not more than one time.
        - Don't forgot to respond with "FINISH", once you receive the answer from workers.
        - The response should be in JSON format.

        **Output Format**
        - The output format should be json: {{'next':<member>}}
        
        ** Example task flow**
        Example1:
        - If user query reqires web sarch then respond with ->{{"next":"web_search_agent"}}.
        - once you receive the response from 'web_search_agent' then respond with :{{"next":"FINISH"}}.
        Example 2:
        - If user query reqires document analysis then respond with ->{{"next":"rag_agent"}}.
        - once you receive the response from 'rag_agent' then respond with :{{"next":"FINISH"}}.
        '''


    # Define router type for structured output
    class Router(TypedDict):
        """Worker to route to next. If no workers needed, route to FINISH."""
        next: Literal["web_search_agent", "rag_agent", "csv_agent", "FINISH"]

    # Create supervisor node function
    def supervisor_node(
        state: GraphState
    ) -> Command[Literal["web_search_agent", "rag_agent", "csv_agent", "__end__"]]:

        # Worker already executed → finish
        if state.get("worker_called"):
            print("--- SUPERVISOR ---")
            print("Worker already called:", state["worker_called"])
            print("Next: FINISH")
            return Command(goto=END)

        messages = [
            {"role": "system", "content": system_prompt},
            *state["messages"]
        ]

        response = agent_model.with_structured_output(Router).invoke(messages)

        print(f"the supervisor raw response: {response}")

        goto = response["next"]

        print("\n--- SUPERVISOR ---")
        print("Next Worker:", goto)

        if goto == "FINISH":
            return Command(goto=END)

        # Save which worker was selected
        return Command(
            update={"worker_called": goto},
            goto=goto
        )



    class AgentState(TypedDict):
        """The state of the agent."""
        messages: Annotated[Sequence[BaseMessage], add_messages]

    def create_agent(llm, tools):
        llm_with_tools = llm.bind_tools(tools)
        def chatbot(state: AgentState):
            return {"messages": [llm_with_tools.invoke(state["messages"])]}

        graph_builder = StateGraph(AgentState)
        graph_builder.add_node("agent", chatbot)

        tool_node = ToolNode(tools=tools)
        graph_builder.add_node("tools", tool_node)

        graph_builder.add_conditional_edges(
            "agent",
            tools_condition,
        )
        graph_builder.add_edge("tools", "agent")
        graph_builder.set_entry_point("agent")
        return graph_builder.compile()




    websearch_agent = create_agent(agent_model, [web_search_tool])

    def web_research_node(
        state: GraphState
    ) -> Command[Literal["supervisor"]]:

        result = websearch_agent.invoke({
            "messages": state["messages"]
        })

        print("\n--- WEB SEARCH AGENT ---")
        print(result)

        return Command(
            update={
                "messages": [
                    AIMessage(
                        content=result["messages"][-1].content,
                        name="web_search_agent"
                    )
                ]
            },
            goto="supervisor"
        )




    rag_agent = create_agent(agent_model, [retriever_tool])

    def rag_node(
        state: GraphState
    ) -> Command[Literal["supervisor"]]:

        result = rag_agent.invoke({
            "messages": state["messages"]
        })

        print("\n--- RAG AGENT ---")
        print(result)

        return Command(
            update={
                "messages": [
                    AIMessage(
                        content=result["messages"][-1].content,
                        name="rag_agent"
                    )
                ]
            },
            goto="supervisor"
        )


    csv_agent = create_agent(agent_model, [csv_agnet_tool])

    def csv_node(
        state: GraphState
    ) -> Command[Literal["supervisor"]]:

        result = csv_agent.invoke({
            "messages": state["messages"]
        })

        print("\n--- CSV AGENT ---")
        print(result)

        return Command(
            update={
                "messages": [
                    AIMessage(
                        content=result["messages"][-1].content,
                        name="csv_agent"
                    )
                ]
            },
            goto="supervisor"
        )

    def guardrail_router(state: GraphState):

        if state["guardrail_decision"] == "ALLOW":
            return "supervisor"

        return "blocked"



    def blocked_node(state: GraphState):
        reason=state["guardrail_reason"]

        return {
            "messages": [
                HumanMessage(
                    content=(
                    reason
                    ),
                    name="guardrail"
                )
            ]
        }


    builder = StateGraph(GraphState)

    builder.add_node("guardrail", guardrail_node)
    builder.add_node("blocked", blocked_node)
    builder.add_node("supervisor", supervisor_node)

    builder.add_node("web_search_agent", web_research_node)
    builder.add_node("rag_agent", rag_node)
    builder.add_node("csv_agent", csv_node)

    builder.add_edge(START, "guardrail")

    builder.add_conditional_edges(
        "guardrail",
        guardrail_router,
        {
            "supervisor": "supervisor",
            "blocked": "blocked"
        }
    )

    graph = builder.compile(checkpointer=checkpointer)

    png_data = graph.get_graph().draw_mermaid_png()

    with open("graph.png", "wb") as f:
        f.write(png_data)

    print("Graph saved as graph.png")


    return graph
        
