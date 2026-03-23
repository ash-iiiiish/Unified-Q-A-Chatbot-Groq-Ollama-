from dataclasses import dataclass
from ollama_model import get_ollama_answer
from groq_model import get_chatgroq_answer

# ── Token limit configuration ──────────────────────────────────────────────────
# Total Groq tokens allowed per session before auto-switching to Ollama.
# Groq free tier: ~500k tokens/day, but per-session we cap at this value
# to avoid burning through the daily quota in a single long conversation.
GROQ_SESSION_TOKEN_LIMIT: int = 10_000


@dataclass
class AnswerResult:
    """Structured return value from get_answer()."""
    response: str           # The model's text answer
    model_used: str         # "chatgroq" or "ollama"
    tokens_this_call: int   # Groq tokens used in this single call (0 for ollama)
    groq_tokens_total: int  # Cumulative Groq tokens used this session
    auto_switched: bool     # True if this call triggered the switch to Ollama
    limit: int              # The configured limit (for display)


# ── Per-session Groq token accumulator ────────────────────────────────────────
# Maps session_id → total Groq tokens consumed so far in that session.
_groq_token_totals: dict[str, int] = {}


def reset_session(session_id: str) -> None:
    """Call this when the user clears the conversation."""
    _groq_token_totals.pop(session_id, None)


def get_groq_session_tokens(session_id: str) -> int:
    return _groq_token_totals.get(session_id, 0)


# ── Main router ────────────────────────────────────────────────────────────────
def get_answer(question: str, model: str, session_id: str) -> AnswerResult:
    """
    Route the question to the selected model.

    If model == "chatgroq" but the session has already consumed ≥ GROQ_SESSION_TOKEN_LIMIT
    tokens, the call is transparently redirected to Ollama and auto_switched is set True.
    """
    current_total = _groq_token_totals.get(session_id, 0)
    auto_switched = False

    # ── Groq path ──────────────────────────────────────────────────────────────
    if model == "chatgroq":
        if current_total >= GROQ_SESSION_TOKEN_LIMIT:
            # Limit already exceeded — redirect silently to Ollama
            auto_switched = True
            response = get_ollama_answer(question, session_id)
            return AnswerResult(
                response=response,
                model_used="ollama",
                tokens_this_call=0,
                groq_tokens_total=current_total,
                auto_switched=auto_switched,
                limit=GROQ_SESSION_TOKEN_LIMIT,
            )

        # Normal Groq call
        response, tokens_this_call = get_chatgroq_answer(question, session_id)

        # Update cumulative counter
        new_total = current_total + tokens_this_call
        _groq_token_totals[session_id] = new_total

        # Check if THIS call pushed us over the limit
        if new_total >= GROQ_SESSION_TOKEN_LIMIT:
            auto_switched = True   # flag so the UI can show the warning banner

        return AnswerResult(
            response=response,
            model_used="chatgroq",
            tokens_this_call=tokens_this_call,
            groq_tokens_total=new_total,
            auto_switched=auto_switched,
            limit=GROQ_SESSION_TOKEN_LIMIT,
        )

    # ── Ollama path ────────────────────────────────────────────────────────────
    elif model == "ollama":
        response = get_ollama_answer(question, session_id)
        return AnswerResult(
            response=response,
            model_used="ollama",
            tokens_this_call=0,
            groq_tokens_total=current_total,
            auto_switched=False,
            limit=GROQ_SESSION_TOKEN_LIMIT,
        )

    # ── Unknown model ──────────────────────────────────────────────────────────
    else:
        return AnswerResult(
            response=f"Unknown model: '{model}'. Please select 'chatgroq' or 'ollama'.",
            model_used=model,
            tokens_this_call=0,
            groq_tokens_total=current_total,
            auto_switched=False,
            limit=GROQ_SESSION_TOKEN_LIMIT,
        )