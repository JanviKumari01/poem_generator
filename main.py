import os
from dotenv import load_dotenv
import google.generativeai as genai
from langgraph.graph import StateGraph, END
from typing import TypedDict

# Load environment variable
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
#print(api_key)

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Define the state schema
class PoemState(TypedDict):
    prompt: str
    poem: str
# Node function: generate a poem
def generate_poem(state: PoemState) -> PoemState:
    prompt = state["prompt"]
    response = model.generate_content(prompt)
    return {"poem": response.text}

# Create state graph with the state schema
builder = StateGraph(PoemState)
builder.add_node("generate", generate_poem)
builder.set_entry_point("generate")
builder.set_finish_point("generate")  # Changed from END to "generate"

graph = builder.compile()

theme = input("Enter a theme or topic for your poem: ")
sarcasm= input("Enter the sarcasm: ")
prompt = f"Write a beautiful and creative poem about theme '{theme} and sarcasm should be {sarcasm}'."

# Run the graph
result = graph.invoke({"prompt": prompt})
print("\nYour poem:\n")
print(result["poem"])