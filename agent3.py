import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()
# Verify Groq API key
if not os.getenv("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it with your Groq API key.")

# Define structured output schema
class ParsedRequest(BaseModel):
    intent: str = Field(description="The identified intent (e.g., create_vm)")
    entities: dict = Field(description="Extracted entities (e.g., {'name': 'dev-box'})")

# Initialize ChatGroq
try:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY"),
        max_retries=2
    )
except Exception as e:
    print(f"Failed to initialize ChatGroq: {e}")
    raise

# Define prompt with escaped JSON syntax
prompt = ChatPromptTemplate.from_messages([
    ("system", """
Parse the user's request into a JSON object with 'intent' and 'entities' for User Input.

Intents:
- create_vm (entities: name, flavor [S.4, M.8])
- resize_vm (entities: name, flavor [M.8, S.4])
- delete_vm (entity: name)
- create_network (entity: name)
- create_volume (entities: name, size [numeric GB])
- delete_volume (entity: name)
- get_usage (no entities)

Examples:
- "Create an S.4 VM named dev-box" → {{"intent": "create_vm", "entities": {{"name": "dev-box", "flavor": "S.4"}}}}
- "What’s my project usage?" → {{"intent": "get_usage", "entities": {{}}}}
- "Invalid request" → {{"intent": "unknown", "entities": {{}}}}

Rules:
- Use exact intent names (e.g., "create_vm").
- Extract entities as strings (e.g., "100" for size).
- Return {{"intent": "unknown", "entities": {{}}}} for unclear inputs.
"""),
    ("human", "{input}")
])

# Create chain
chain = prompt | llm.with_structured_output(ParsedRequest, include_raw=False)

# Test inputs
test_inputs = [
    "Create an S.4 VM named dev-box",
    "Create a  VM Named Satvik-box",
    "Resize dev-box to flavor M.8",
    "Delete the VM dev-box",
    "Create a private network called blue-net",
    "Create a 100 GB volume named data-disk",
    "Delete volume data-disk",
    "What’s my project usage?",
    "Invalid request"
]

# Run tests
for user_input in test_inputs:
    try:
        result = chain.invoke({"input": user_input})
        print(f"Input: {user_input}")
        print(f"Intent: {result.intent}")
        print(f"Entities: {result.entities}")
    except Exception as e:
        print(f"Input: {user_input}")
        print(f"Intent: unknown")
        print(f"Entities: {{}}")
        print(f"Error: {e}")
    print("-" * 50)