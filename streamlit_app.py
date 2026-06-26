import streamlit as st
from final import ask_legal_ai

st.set_page_config(page_title="Legal AI Advisor", layout="wide")

st.title("⚖️ Legal AI Advisor (BNS Based)")

question = st.text_input("Type your legal question here...")

if st.button("Ask"):
    if question.strip():
        with st.spinner("Analyzing..."):
            response = ask_legal_ai(question)

            st.markdown(f"### 🧑 You\n{question}")
            st.markdown(response)