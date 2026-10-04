"""Grounded answer generation: the 'G' of RAG.

The LLM receives ONLY the retrieved chunks as context and is instructed to
answer strictly from them, replying NOT_IN_KB when the context is missing
the answer. That output is mapped to the polite fallback, so the bot never
invents facts beyond the knowledge base.
"""
import re

from ..logger import get_logger
from .llm import llm_service

log = get_logger("knowbot.rag")

SYSTEM_PROMPT = """You are KnowBot, a precise knowledge-base assistant.

Rules you must always follow:
1. Answer ONLY using facts contained in the CONTEXT provided by the user.
2. Never use outside knowledge, never guess, never invent names or numbers.
3. If the CONTEXT does not contain the information needed to answer, reply
   with exactly this single token: NOT_IN_KB
4. Be concise and helpful (2-6 sentences). Use a short list when the user
   asks for several items.
5. Answer in the same language as the question.
"""

USER_PROMPT_TEMPLATE = """CONTEXT (extracts from my knowledge base):

{context}

QUESTION: {question}

Answer (or NOT_IN_KB):"""

_REFUSAL_PATTERN = re.compile(
    r"NOT_IN_KB|not\s+(?:be\s+)?(?:able to|mentioned|found|contained|included)|"
    r"doesn'?t\s+(?:appear|contain|mention)|do(?:es)?\s?not\s+(?:appear|contain|mention)|"
    r"no information|i don'?t have|i do not have|cannot find|can't find|not specified|"
    r"not provided|not available in|outside (?:of )?(?:my |the )?knowledge",
    re.IGNORECASE,
)


def extract_text(response) -> str:
    """Normalize an LLM response to plain text.

    Depending on the model/SDK version, `response.content` is either a string
    or a list of content blocks like [{"type": "text", "text": "..."}].
    """
    content = getattr(response, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        return "".join(parts)
    return str(content or "")


def generate_answer(question: str, documents: list) -> dict | None:
    """Generate an answer grounded in the retrieved documents.

    Returns {"answer", "grounded": True} or None when the LLM (or the
    caller should) answer that the knowledge base does not cover it.
    """
    if not documents:
        return None
    context = "\n\n".join(
        f"[Source: {doc.metadata.get('filename', 'unknown')}]\n{doc.page_content}"
        for doc in documents
    )
    prompt = USER_PROMPT_TEMPLATE.format(context=context, question=question)
    response = llm_service.get().invoke(prompt)
    text = extract_text(response).strip()
    # Strip possible markdown fences the model might add.
    if text.startswith("```"):
        text = text.strip("`\n")
        if text.startswith(("json", "text")):
            text = text.split("\n", 1)[-1]

    if _REFUSAL_PATTERN.search(text) and len(text) < 400:
        log.info("LLM refused (answer not in context): %r", text[:120])
        return None
    return {"answer": text, "grounded": True}
