import streamlit as st
from parser_backend import process_user_input
from aiagent import create_vm  # <-- Add more handlers as needed

st.title("Cloud Assistant")

user_input = st.text_input("Enter your cloud instruction:")
if user_input:
    parsed = process_user_input(user_input)
    st.write("Parsed Intent:", parsed)

    intent = parsed.get("intent")
    entities = parsed.get("entities", {})

    if intent == "create_vm":
        name = entities.get("name")
        flavor = entities.get("flavor")
        if name and flavor:
            result = create_vm(name, flavor)
            st.success(result)
        else:
            st.error("Missing VM name or flavor.")
    elif intent == "resize_vm":
        st.warning("Resize VM not implemented yet.")
    elif intent == "error":
        st.error("Could not understand input.")
