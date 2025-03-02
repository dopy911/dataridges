import streamlit as st
from src.chatbot import Chatbot
from src.query_executor import QueryExecutor
from src.report_generator import ReportGenerator

import datetime
import time

# Initialize components
chatbot = Chatbot()
query_executor = QueryExecutor()
report_generator = ReportGenerator()

# Streamlit UI
st.title("Smart Chatbot")

# Append to chat history
user_input = st.chat_input("Ask your question:")
if user_input:
    # Get current timestamp
    timestamp = time.time()
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    formatted_datetime = dt_object.strftime("%Y-%m-%d %H:%M")
    # Append user input
    st.session_state["chat_history"].append(
        {
            "role": "human",
            "content": user_input,
            "time": formatted_datetime,
        },
    )
else:
    print("no user input yet!")

# Display chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
for i in st.session_state["chat_history"]:
    with st.chat_message(name=i["role"]):
        st.markdown(i["content"])


    # query = chatbot.generate_query(user_input)
    # st.write(f"Generated Query: {query}")
    
    # results = query_executor.execute(query)
    # st.write("Query Results:")
    # st.dataframe(results)
    
    # st.write("Visualization:")
    # report_generator.generate(results, streamlit=True)

