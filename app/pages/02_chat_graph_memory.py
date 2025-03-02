from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_openai import ChatOpenAI
# from langchain_community.callbacks.streamlit import (
#     StreamlitCallbackHandler,
# )
from util.callback_fix import get_streamlit_cb

from langchain_community.tools.tavily_search import TavilySearchResults

import streamlit as st
import json
import os

# Define memory
from langgraph.checkpoint.memory import MemorySaver

# Define a tool 
from langchain_core.messages import ToolMessage

os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

tool = TavilySearchResults(max_results=2)
tools = [tool]

# Add tool node to the graph
tool_node = ToolNode(tools=[tool])

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

if "tools" not in st.session_state:
    # Define the chatbot node
    llm = ChatOpenAI(model_name="gpt-4") #, model_kwargs={"response_format": {"type": "json_object"}})
    # Modification: tell the LLM which tools it can call
    llm_with_tools = llm.bind_tools(tools)
    st.session_state["tools"] = llm_with_tools

def chatbot(state: State):
    return {"messages": [st.session_state["tools"].invoke(state["messages"])]}

if "graph" not in st.session_state:
    # Define the graph
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)
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
        st.write(response)
        st.write(st.session_state["graph"].get_state_history({"configurable": {"thread_id": "1"}}))
    st.session_state.messages.append({"role": "assistant", "content": response})
