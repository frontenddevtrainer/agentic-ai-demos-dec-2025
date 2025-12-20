from __future__ import annotations

import json
from typing import Literal, TypedDict

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.graph import END, StateGraph

from config import Settings
from kb_store import load_vectorstore


AGENTIC_KEYWORDS = {
    "agentic",
    "agent",
    "agents",
    "langgraph",
    "langchain",
    "rag",
    "retrieval",
    "tool",
    "tools",
    "planner",
    "planning",
    "memory",
    "workflow",
    "orchestration",
    "multi-agent",
    "chain of thought",
}
PYTHON_KEYWORDS = {
    "python",
    "pip",
    "venv",
    "virtualenv",
    "traceback",
    "exception",
    "error",
    "list comprehension",
    "dict",
    "pandas",
    "asyncio",
    "fastapi",
    "flask",
    "pytest",
    "type hints",
    "typing",
}


class AgentState(TypedDict, total=False):
    question: str
    allowed: bool
    topic: Literal["agentic_ai", "python", "other"]
    docs: list[Document]
    answer: str


def _precheck(text: str) -> bool:
    lower = text.lower()
    if not lower.strip():
        return False
    if "```" in text:
        return True
    if any(key in lower for key in AGENTIC_KEYWORDS | PYTHON_KEYWORDS):
        return True
    if "?" in text and ("ai" in lower or "code" in lower):
        return True
    return False


def _safe_json_loads(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def build_graph(settings: Settings):
    embeddings = OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
    )
    vectorstore = load_vectorstore(settings.vectorstore_dir, embeddings)

    classifier_llm = ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_classifier_model,
        temperature=0,
    )
    answer_llm = ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=0.2,
    )

    def classify(state: AgentState) -> AgentState:
        question = state.get("question", "").strip()
        if not _precheck(question):
            return {"allowed": False, "topic": "other"}

        messages = [
            (
                "system",
                "You are a strict topic filter. Reply with JSON only: "
                '{"allowed": true|false, "topic": "agentic_ai"|"python"|"other"}. '
                "Allow only agentic AI and Python questions. If uncertain, set allowed false.",
            ),
            (
                "human",
                f"Message: {question}",
            ),
        ]
        response = classifier_llm.invoke(messages)
        data = _safe_json_loads(response.content.strip())
        topic = data.get("topic", "other")
        allowed = bool(data.get("allowed")) and topic in {"agentic_ai", "python"}
        return {"allowed": allowed, "topic": topic}

    def retrieve(state: AgentState) -> AgentState:
        question = state.get("question", "")
        docs = vectorstore.similarity_search(question, k=settings.top_k)
        return {"docs": docs}

    def answer(state: AgentState) -> AgentState:
        question = state.get("question", "")
        docs = state.get("docs", [])
        context_lines = []
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            context_lines.append(f"Source: {source}\n{doc.page_content}")
        context = "\n\n".join(context_lines) if context_lines else ""

        system_prompt = (
            "You are the AgenticAI Trainer. Answer only agentic AI and Python questions. "
            "Use the KB context provided. If the KB does not contain the answer, say you "
            "don't have it in the KB and suggest adding a document. Keep replies concise "
            "and practical. Include a short 'Sources:' line when you used KB context."
        )

        human_prompt = (
            f"Question: {question}\n\n"
            f"KB Context:\n{context}" if context else f"Question: {question}\n\nKB Context: (empty)"
        )

        response = answer_llm.invoke([
            ("system", system_prompt),
            ("human", human_prompt),
        ])
        return {"answer": response.content.strip()}

    graph = StateGraph(AgentState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("classify", classify)
    graph.add_node("answer", answer)

    graph.set_entry_point("classify")

    def route(state: AgentState) -> str:
        return "retrieve" if state.get("allowed") else "end"

    graph.add_conditional_edges("classify", route, {"retrieve": "retrieve", "end": END})
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


def answer_question(graph, question: str) -> str | None:
    result = graph.invoke({"question": question})
    if not result.get("allowed"):
        return None
    return result.get("answer")