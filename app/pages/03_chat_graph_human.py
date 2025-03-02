from typing import Annotated

from typing_extensions import TypedDict
from langchain_core.tools import tool

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_openai import ChatOpenAI
from util.callback_fix import get_streamlit_cb

from langchain_community.tools.tavily_search import TavilySearchResults

import streamlit as st
import json
import os

# Define memory
from langgraph.checkpoint.memory import MemorySaver

# Define a tool 
from langchain_core.messages import ToolMessage, HumanMessage

# Define humamn tools
from langgraph.types import Command, interrupt


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

# human tools
@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]

if "tools" not in st.session_state:
    os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]
    tool = TavilySearchResults(max_results=2)
    tools = [tool, human_assistance]
    st.session_state["tools"] = tools
# LLM with tools binding for the graph

if "llm" not in st.session_state:
    # Define the chatbot node
    llm = ChatOpenAI(model_name="gpt-4") #, model_kwargs={"response_format": {"type": "json_object"}})
    # Modification: tell the LLM which tools it can call
    llm_with_tools = llm.bind_tools(st.session_state["tools"])
    st.session_state["llm"] = llm_with_tools

def chatbot(state: State):
    return {"messages": [st.session_state["llm"].invoke(state["messages"])]}


if "graph" not in st.session_state:
    # Define the graph
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode(st.session_state["tools"]))
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    # Any time a tool is called, we return to the chatbot to decide the next step
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")

    mem = MemorySaver()
    st.session_state["graph"] = graph_builder.compile(checkpointer=mem)
    st.image(st.session_state["graph"].get_graph().draw_mermaid_png())

def stream_graph_updates(user_input: str, st_callback):
    config = {"callbacks": [st_callback], "configurable": {"thread_id": "1"}}
    response = st.session_state["graph"].invoke({"messages": [{"role": "user", "content": user_input}]}, config)
    print(st.session_state["graph"].get_state(config))
    return response["messages"][-1].content


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        st_callback = get_streamlit_cb(st.empty())
        response = stream_graph_updates(prompt, st_callback)
        #if response type of HumanMessage
        st.write(response.content)
        #st.write(st.session_state["graph"].get_state_history({"configurable": {"thread_id": "1"}}))
    st.session_state.messages.append({"role": "assistant", "content": response})
