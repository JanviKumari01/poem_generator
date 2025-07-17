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
class PoemQuoteState(TypedDict):
    choice: str
    theme: str
    sarcasm: str
    poem: str
    quotes: str

# Conditional edge function: decide what to generate based on user choice
def decide_generation(state: PoemQuoteState) -> str:
    choice = state["choice"].lower()
    if "poem" in choice:
        return "poem_node"
    elif "quote" in choice:
        return "quote_node"
    else:
        return "poem_node"  # default to poem

# Node function: generate a poem
def generate_poem(state: PoemQuoteState) -> PoemQuoteState:
    theme = state["theme"]
    sarcasm = state["sarcasm"]
    prompt = f"Write a beautiful and creative poem about theme '{theme}' and sarcasm should be {sarcasm}."
    response = model.generate_content(prompt)
    return {"poem": response.text}

# Node function: generate a quote
def generate_quote(state: PoemQuoteState) -> PoemQuoteState:
    theme = state["theme"]
    sarcasm = state["sarcasm"]
    quote_prompt = f"Generate an inspirational quote about '{theme}' with {sarcasm} level of sarcasm."
    response = model.generate_content(quote_prompt)
    return {"quotes": response.text}

# Dummy start node to handle the conditional routing
def start_node(state: PoemQuoteState) -> PoemQuoteState:
    return state  # Just pass through the state

# Create state graph with the state schema
builder = StateGraph(PoemQuoteState)
builder.add_node("start", start_node)
builder.add_node("poem_node", generate_poem)
builder.add_node("quote_node", generate_quote)

# Add conditional edges from start node
builder.add_conditional_edges(
    "start",
    decide_generation,
    {
        "poem_node": "poem_node",
        "quote_node": "quote_node"
    }
)

# Add edges to END from both generation nodes
builder.add_edge("poem_node", END)
builder.add_edge("quote_node", END)

builder.set_entry_point("start")

graph = builder.compile()

# Get user input
choice = input("What would you like to generate? (poem/quote): ")
theme = input("Enter a theme or topic: ")
sarcasm = input("Enter the sarcasm level: ")

# Run the graph
result = graph.invoke({
    "choice": choice,
    "theme": theme,
    "sarcasm": sarcasm,
    "poem": "",
    "quotes": ""
})

# Display results based on what was generated
if result.get("poem"):
    print("\nYour poem:\n")
    print(result["poem"])
elif result.get("quotes"):
    print("\nYour quote:\n")
    print(result["quotes"])