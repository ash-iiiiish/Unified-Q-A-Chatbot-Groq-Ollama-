from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from dotenv import load_dotenv

load_dotenv()

# ── Token Counter Callback ─────────────────────────────────────────────────────
class TokenCounterCallback(BaseCallbackHandler):
    """Captures token usage reported by the Groq API after each LLM call."""

    def __init__(self) -> None:
        self.last_call_tokens: int = 0

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Extract total_tokens from Groq's llm_output metadata."""
        try:
            usage = (response.llm_output or {}).get("token_usage", {})
            self.last_call_tokens = int(usage.get("total_tokens", 0))
        except Exception:
            self.last_call_tokens = 0


# ── Shared callback instance (module-level, reused across calls) ───────────────
_token_counter = TokenCounterCallback()

# ── Session store ──────────────────────────────────────────────────────────────
_session_store: dict[str, ChatMessageHistory] = {}


def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in _session_store:
        _session_store[session_id] = ChatMessageHistory()
    return _session_store[session_id]


# ── Model & Chain ──────────────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    callbacks=[_token_counter],
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are Lumina, a refined and helpful AI assistant. "
        "Provide clear, thoughtful, and concise answers.",
    ),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

chain = prompt | llm | StrOutputParser()

chat_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)


# ── Public API ─────────────────────────────────────────────────────────────────
def get_chatgroq_answer(question: str, session_id: str) -> tuple[str, int]:
    """
    Returns:
        answer      – the model's text response
        tokens_used – total tokens consumed by this single call
    """
    _token_counter.last_call_tokens = 0          # reset before each call
    answer = chat_chain.invoke(
        {"question": question},
        config={"configurable": {"session_id": session_id}},
    )
    return answer, _token_counter.last_call_tokens