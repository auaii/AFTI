import os
from dotenv import load_dotenv
from typing_extensions import Annotated, Literal
from langchain import tools
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI
from deepagents import create_deep_agent
from tools import tavily_search, think_tool
from prompts import TESTING_PROTOCOL_PROMPT

# Import Library สำหรับ Pretty Print
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

load_dotenv()

# Model Gemini3
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0)

agent = create_deep_agent(
    system_prompt = TESTING_PROTOCOL_PROMPT,
    model = model,
    tools = [tavily_search, think_tool]
)

result = agent.invoke({"messages": [{"role": "user", "content": "I found a 'Missing Hole' defect on a Double-Sided PCB. Please provide a testing protocol"}]})

console = Console()

content = result["messages"][-1].content
console.print(Panel(Markdown(content), title="📝 Testing Protocol Report", expand=False, border_style="green"))