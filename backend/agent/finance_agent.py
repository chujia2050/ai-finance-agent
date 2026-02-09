"""LangChain-based financial analysis agent with autonomous tool use."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from sqlalchemy.orm import Session
from agent.tools import create_tools
import os

SYSTEM_PROMPT = """You are an expert financial analyst AI agent. You have access to a set of
tools that let you query, analyze, and compare financial data from uploaded datasets.

Your capabilities:
- Query specific financial data points (revenue, expenses, assets, etc.)
- Calculate financial ratios (profitability, liquidity, leverage)
- Analyze trends across periods
- Detect anomalies and outliers
- Compare periods side-by-side
- Provide data summaries

When answering questions:
1. Always use your tools to get actual data before responding — never guess or make up numbers.
2. Provide specific numbers and cite the periods they come from.
3. Explain financial concepts in clear, professional language.
4. When asked for recommendations, base them on the data and standard financial analysis.
5. Format numbers with commas and appropriate units (%, $, x).
6. If the data doesn't contain what's needed, say so clearly.

You are assisting finance professionals, so maintain a professional tone while being thorough."""


def create_finance_agent(db: Session, dataset_id: int) -> AgentExecutor:
    """Create a LangChain agent with financial analysis tools."""
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    tools = create_tools(db, dataset_id)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=8,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )

    return executor


async def run_agent(db: Session, dataset_id: int, message: str, chat_history: list = None) -> dict:
    """Run the financial agent with a user message and return the response."""
    executor = create_finance_agent(db, dataset_id)

    history_messages = []
    if chat_history:
        for msg in chat_history:
            if msg["role"] == "user":
                history_messages.append(HumanMessage(content=msg["message"]))
            else:
                history_messages.append(AIMessage(content=msg["message"]))

    result = await executor.ainvoke({
        "input": message,
        "chat_history": history_messages,
    })

    tools_used = []
    for step in result.get("intermediate_steps", []):
        if hasattr(step[0], "tool"):
            tools_used.append(step[0].tool)

    return {
        "response": result["output"],
        "tools_used": list(set(tools_used)),
    }
