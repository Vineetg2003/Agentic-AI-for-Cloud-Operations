import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq  # Correct import from langchain_groq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableMap

load_dotenv()

# Validate API key presence
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not set in .env")

# Set up the LLM
llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0,
    api_key=api_key
)

# Define the prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Parse user input into JSON with 'intent' and 'entities'. Valid intents: create_vm, delete_vm, etc."),
    ("human", "{input}")
])

# Define the parser
parser = JsonOutputParser()

# Final chain
chain = prompt | llm | parser

# Function to call
def process_user_input(user_input):
    return chain.invoke({"input": user_input})
