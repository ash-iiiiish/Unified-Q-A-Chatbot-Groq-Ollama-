import streamlit as st
import uuid
from switch_model import get_answer, reset_session, GROQ_SESSION_TOKEN_LIMIT

st.set_page_config(
    page_title="Unified Chatbot",
    page_icon="🤖",
    layout="centered",
)

# ── Dark Theme CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

/* ── Root Variables ── */
:root {
    --bg:           #0D0F12;
    --bg2:          #13161B;
    --bg3:          #1A1E25;
    --bg4:          #222731;
    --border:       #2A2F3A;
    --border2:      #353B48;
    --text:         #E2E6EF;
    --text-muted:   #7A8494;
    --text-dim:     #4A5262;
    --accent:       #4F8EF7;
    --accent2:      #3B72D4;
    --accent-glow:  rgba(79,142,247,0.18);
    --accent-pale:  rgba(79,142,247,0.08);
    --green:        #3DDC97;
    --green-pale:   rgba(61,220,151,0.10);
    --amber:        #F0A500;
    --amber-pale:   rgba(240,165,0,0.10);
    --red:          #F05252;
    --red-pale:     rgba(240,82,82,0.10);
    --user-bg:      #1C2333;
    --shadow-sm:    0 1px 4px rgba(0,0,0,0.4);
    --shadow-md:    0 4px 20px rgba(0,0,0,0.5);
    --radius:       12px;
    --radius-sm:    8px;
    --radius-pill:  999px;
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
    background-image:
        radial-gradient(ellipse at 70% 0%, rgba(79,142,247,0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 20% 100%, rgba(61,220,151,0.04) 0%, transparent 45%) !important;
    min-height: 100vh;
}

.main .block-container {
    max-width: 780px !important;
    padding: 2rem 1.75rem 6.5rem 1.75rem !important;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

/* ── Headings ── */
h1 {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 1.55rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    color: var(--text) !important;
    margin-bottom: 0 !important;
}

h2, h3 {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text) !important;
}

/* ── Page header strip ── */
.page-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1.6rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}
.page-header .bot-icon {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-sm);
    background: var(--bg3);
    border: 1px solid var(--border2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}
.page-header .title-block h1 {
    font-size: 1.2rem !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}
.page-header .title-block .sub {
    font-size: 0.72rem;
    color: var(--text-muted);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 2px;
    font-family: 'IBM Plex Mono', monospace;
}
.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 6px var(--green);
    display: inline-block;
    margin-right: 5px;
    animation: blink 2.5s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {
    margin-bottom: 0.5rem !important;
}

/* User bubble */
[data-testid="stChatMessage"][aria-label*="user"] > div {
    background: var(--user-bg) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius) var(--radius) 3px var(--radius) !important;
    padding: 0.85rem 1.1rem !important;
    box-shadow: var(--shadow-sm) !important;
    max-width: 82% !important;
    margin-left: auto !important;
}

/* Assistant bubble */
[data-testid="stChatMessage"][aria-label*="assistant"] > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) var(--radius) var(--radius) 3px !important;
    padding: 0.85rem 1.1rem !important;
    box-shadow: var(--shadow-sm) !important;
    max-width: 88% !important;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {
    font-size: 0.91rem !important;
    line-height: 1.68 !important;
    color: var(--text) !important;
}

[data-testid="stChatMessage"] code {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    background: var(--bg4) !important;
    border: 1px solid var(--border) !important;
    padding: 1px 5px !important;
    border-radius: 4px !important;
    color: var(--accent) !important;
}

/* ── Chat Input ── */
[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: min(780px, 92vw) !important;
    padding: 0.9rem 1rem 1.1rem !important;
    background: linear-gradient(to top, var(--bg) 75%, transparent) !important;
    z-index: 999 !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    padding: 0.75rem 1rem !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.91rem !important;
    color: var(--text) !important;
    box-shadow: var(--shadow-sm) !important;
    transition: border-color 0.18s, box-shadow 0.18s !important;
}

[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInput"] input::placeholder {
    color: var(--text-dim) !important;
}

[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
    outline: none !important;
}

[data-testid="stChatInput"] button {
    background: var(--accent) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(79,142,247,0.35) !important;
    transition: background 0.15s, box-shadow 0.15s !important;
}

[data-testid="stChatInput"] button:hover {
    background: var(--accent2) !important;
    box-shadow: 0 4px 14px rgba(79,142,247,0.45) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] > div {
    padding: 1.8rem 1.3rem !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    border-bottom: 1px solid var(--border) !important;
    padding-bottom: 0.6rem !important;
    margin-bottom: 0.9rem !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

/* ── Radio ── */
[data-testid="stRadio"] > div {
    gap: 4px !important;
    display: flex !important;
    flex-direction: column !important;
}

[data-testid="stRadio"] label {
    font-size: 0.87rem !important;
    color: var(--text-muted) !important;
    padding: 0.5rem 0.8rem !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid transparent !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
}

[data-testid="stRadio"] label:hover {
    background: var(--bg4) !important;
    color: var(--text) !important;
    border-color: var(--border2) !important;
}

/* ── Token Meter ── */
.token-meter-wrap {
    margin-top: 1.2rem;
}
.token-meter-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 6px;
}
.token-meter-label {
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    font-family: 'IBM Plex Mono', monospace;
}
.token-meter-count {
    font-size: 0.72rem;
    font-weight: 500;
    font-family: 'IBM Plex Mono', monospace;
    font-variant-numeric: tabular-nums;
}
.token-meter-track {
    width: 100%;
    height: 5px;
    background: var(--bg4);
    border-radius: 99px;
    overflow: hidden;
    border: 1px solid var(--border);
}
.token-meter-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.45s ease;
}
.token-meter-fill.ok      { background: linear-gradient(90deg, #3DDC97, #56E8AA); }
.token-meter-fill.warning { background: linear-gradient(90deg, #F0A500, #F7C040); }
.token-meter-fill.danger  { background: linear-gradient(90deg, #F05252, #F47878); }
.token-meter-sub {
    margin-top: 4px;
    font-size: 0.67rem;
    color: var(--text-dim);
    font-family: 'IBM Plex Mono', monospace;
    text-align: right;
}

/* ── Model info card ── */
.model-card {
    margin-top: 0.9rem;
    padding: 0.8rem;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    font-size: 0.78rem;
    color: var(--text-muted);
    line-height: 1.55;
}
.model-card .model-name {
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 2px;
}
.model-card .model-tag {
    display: inline-block;
    font-size: 0.66rem;
    font-family: 'IBM Plex Mono', monospace;
    background: var(--accent-pale);
    color: var(--accent);
    border: 1px solid rgba(79,142,247,0.2);
    padding: 1px 7px;
    border-radius: var(--radius-pill);
    margin-bottom: 6px;
    letter-spacing: 0.04em;
}
.model-card .warn-tag {
    display: inline-block;
    font-size: 0.66rem;
    font-family: 'IBM Plex Mono', monospace;
    background: var(--amber-pale);
    color: var(--amber);
    border: 1px solid rgba(240,165,0,0.25);
    padding: 1px 7px;
    border-radius: var(--radius-pill);
    margin-bottom: 6px;
    letter-spacing: 0.04em;
}

/* ── Auto-switch Banner ── */
.switch-banner {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 0.85rem 1rem;
    background: var(--amber-pale);
    border: 1px solid rgba(240,165,0,0.2);
    border-left: 3px solid var(--amber);
    border-radius: var(--radius-sm);
    margin-bottom: 1.2rem;
    animation: fadein 0.3s ease;
}
.switch-banner .icon { font-size: 1rem; flex-shrink: 0; margin-top: 1px; }
.switch-banner .text { font-size: 0.8rem; line-height: 1.55; color: #C8920A; }
.switch-banner .text strong { font-weight: 600; display: block; margin-bottom: 2px; color: var(--amber); }

@keyframes fadein {
    from { opacity: 0; transform: translateY(-5px); }
    to   { opacity: 1; transform: translateY(0);    }
}

/* ── Sidebar clear button ── */
[data-testid="stSidebar"] button {
    background: var(--bg4) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text-muted) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.83rem !important;
    transition: all 0.15s !important;
}
[data-testid="stSidebar"] button:hover {
    background: var(--red-pale) !important;
    border-color: var(--red) !important;
    color: var(--red) !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Thinking dots ── */
.thinking-dots { display: inline-flex; gap: 5px; align-items: center; padding: 0.4rem 0; }
.thinking-dots span {
    width: 5px; height: 5px;
    background: var(--accent); border-radius: 50%;
    animation: pdot 1.1s ease-in-out infinite;
    opacity: 0.3;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.18s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.36s; }
@keyframes pdot {
    0%, 100% { opacity: 0.2; transform: scale(0.8); }
    50%       { opacity: 1;   transform: scale(1.15); }
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 1rem 3rem;
    color: var(--text-dim);
}
.empty-state .icon {
    font-size: 2.2rem;
    margin-bottom: 1rem;
    opacity: 0.25;
}
.empty-state .title {
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text-muted);
    margin-bottom: 0.4rem;
}
.empty-state .sub {
    font-size: 0.8rem;
    line-height: 1.6;
    max-width: 280px;
    margin: 0 auto;
}
.empty-state .hint {
    margin-top: 1.2rem;
    font-size: 0.72rem;
    font-family: 'IBM Plex Mono', monospace;
    color: var(--accent);
    letter-spacing: 0.04em;
    opacity: 0.7;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent2); }
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "groq_tokens_used" not in st.session_state:
    st.session_state.groq_tokens_used = 0
if "show_switch_banner" not in st.session_state:
    st.session_state.show_switch_banner = False
if "model_choice" not in st.session_state:
    st.session_state.model_choice = "chatgroq"


# ── Helpers ────────────────────────────────────────────────────────────────────
def _token_bar_html(used: int, limit: int) -> str:
    pct = min(used / limit * 100, 100) if limit else 0
    if pct < 60:
        state, color = "ok", "#3DDC97"
    elif pct < 85:
        state, color = "warning", "#F0A500"
    else:
        state, color = "danger", "#F05252"
    remaining = max(limit - used, 0)
    return f"""
    <div class="token-meter-wrap">
        <div class="token-meter-header">
            <span class="token-meter-label">Groq Tokens</span>
            <span class="token-meter-count" style="color:{color};">{used:,} / {limit:,}</span>
        </div>
        <div class="token-meter-track">
            <div class="token-meter-fill {state}" style="width:{pct:.1f}%;"></div>
        </div>
        <div class="token-meter-sub">{remaining:,} remaining</div>
    </div>
    """


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Model")

    locked = st.session_state.groq_tokens_used >= GROQ_SESSION_TOKEN_LIMIT
    radio_index = 1 if locked else (0 if st.session_state.model_choice == "chatgroq" else 1)

    model_choice = st.radio(
        "model",
        ["chatgroq", "ollama"],
        index=radio_index,
        disabled=locked,
        label_visibility="collapsed",
    )

    if not locked:
        st.session_state.model_choice = model_choice
    else:
        model_choice = "ollama"

    model_meta = {
        "chatgroq": ("⚡", "Llama 3.1 · 8B Instant", "Groq Cloud", False),
        "ollama":   ("🖥", "Gemma 3",                 "Ollama · Local", True),
    }
    icon, name, provider, is_free = model_meta[model_choice]
    tag_class = "warn-tag" if locked else "model-tag"
    tag_text  = "⚠ limit reached — auto switched" if locked else provider

    st.markdown(f"""
    <div class="model-card">
        <div class="model-name">{icon} &nbsp;{name}</div>
        <span class="{tag_class}">{tag_text}</span>
        <div>{'Free &amp; unlimited — running locally.' if is_free else 'Fast cloud inference via Groq API.'}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(_token_bar_html(
        st.session_state.groq_tokens_used,
        GROQ_SESSION_TOKEN_LIMIT,
    ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑  Clear conversation", use_container_width=True):
        reset_session(st.session_state.session_id)
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.groq_tokens_used = 0
        st.session_state.show_switch_banner = False
        st.session_state.model_choice = "chatgroq"
        st.rerun()


# ── Page header ────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <div class="bot-icon">🤖</div>
    <div class="title-block">
        <h1>Unified Chatbot</h1>
        <div class="sub"><span class="status-dot"></span>online · {model_choice}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Auto-switch banner ─────────────────────────────────────────────────────────
if st.session_state.show_switch_banner:
    st.markdown(f"""
    <div class="switch-banner">
        <div class="icon">⚡</div>
        <div class="text">
            <strong>Auto-switched to Ollama (local)</strong>
            Groq session hit the {GROQ_SESSION_TOKEN_LIMIT:,}-token limit.
            Now running on Gemma 3 locally — free &amp; unlimited.
            Clear the conversation to reset.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Chat history ───────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">🤖</div>
        <div class="title">No messages yet</div>
        <div class="sub">Ask anything. Switch models from the sidebar anytime.</div>
        <div class="hint">↓ type your message below</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ── Input ──────────────────────────────────────────────────────────────────────
user_input = st.chat_input("Message…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner(""):
            st.markdown("""
            <div class="thinking-dots"><span></span><span></span><span></span></div>
            """, unsafe_allow_html=True)
            result = get_answer(
                user_input,
                model_choice,
                st.session_state.session_id,
            )
        st.markdown(result.response)

    st.session_state.groq_tokens_used = result.groq_tokens_total
    if result.auto_switched and not st.session_state.show_switch_banner:
        st.session_state.show_switch_banner = True
        st.session_state.model_choice = "ollama"

    st.session_state.messages.append({"role": "assistant", "content": result.response})
    st.rerun()