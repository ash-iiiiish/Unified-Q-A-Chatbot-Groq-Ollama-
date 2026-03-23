import streamlit as st
import uuid
from switch_model import get_answer, reset_session, GROQ_SESSION_TOKEN_LIMIT

st.set_page_config(
    page_title="Unified Chatbot",
    page_icon="🤖",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Syne:wght@600;700;800&family=Inter:wght@300;400;500;600&display=swap');

/* ══════════════════════════════════════════
   TOKENS
══════════════════════════════════════════ */
:root {
    --bg:         #212121;
    --bg-sidebar: #171717;
    --bg-input:   #2F2F2F;
    --bg-user:    #2F2F2F;
    --bg-bot:     #212121;
    --border:     #3A3A3A;
    --border2:    #444;
    --text:       #ECECEC;
    --text-soft:  #B0B0B0;
    --text-muted: #787878;
    --text-dim:   #4A4A4A;
    --accent:     #5B9BF8;
    --accent2:    #3D7DEE;
    --accent-g:   rgba(91,155,248,0.18);
    --accent-p:   rgba(91,155,248,0.08);
    --green:      #3DDC97;
    --green-g:    rgba(61,220,151,0.3);
    --amber:      #FBBF24;
    --amber-p:    rgba(251,191,36,0.10);
    --red:        #F87171;
    --red-p:      rgba(248,113,113,0.10);
    --r:          14px;
    --r-sm:       10px;
    --r-pill:     999px;
}

/* ══════════════════════════════════════════
   GLOBAL
══════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
    font-size: 16px !important;
}

.stApp {
    background: var(--bg) !important;
    min-height: 100vh;
}

.main .block-container {
    max-width: 800px !important;
    padding: 1.5rem 1.5rem 7rem 1.5rem !important;
}

header[data-testid="stHeader"] { background: transparent !important; }

/* ══════════════════════════════════════════
   PAGE HEADER  (ChatGPT-style top bar)
══════════════════════════════════════════ */
.page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.9rem 0;
    margin-bottom: 1.2rem;
    border-bottom: 1px solid var(--border);
}
.page-header .left {
    display: flex;
    align-items: center;
    gap: 10px;
}
.page-header .bot-icon {
    width: 36px; height: 36px;
    border-radius: 8px;
    background: #2A2A2A;
    border: 1px solid var(--border2);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.page-header h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    margin: 0 !important;
    letter-spacing: -0.01em !important;
}
.page-header .model-pill {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--accent);
    background: var(--accent-p);
    border: 1px solid rgba(91,155,248,0.25);
    padding: 3px 10px;
    border-radius: var(--r-pill);
}
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green-g);
    display: inline-block;
    animation: blink 2.5s ease-in-out infinite;
}
@keyframes blink {
    0%,100% { opacity:1; }
    50%      { opacity:0.35; }
}

/* ══════════════════════════════════════════
   CHAT MESSAGES — ChatGPT layout
   user = RIGHT,  assistant = LEFT
══════════════════════════════════════════ */

/* Remove streamlit default row layout */
[data-testid="stChatMessage"] {
    display: flex !important;
    flex-direction: row !important;
    gap: 0 !important;
    padding: 0 !important;
    margin-bottom: 1.1rem !important;
    background: transparent !important;
    border: none !important;
}

/* ── USER: push to the RIGHT ── */
[data-testid="stChatMessage"][aria-label*="user"] {
    justify-content: flex-end !important;
}
[data-testid="stChatMessage"][aria-label*="user"] > div {
    background: var(--bg-user) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 0.85rem 1.15rem !important;
    max-width: 72% !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.35) !important;
    animation: msg-in-right 0.25s cubic-bezier(0.34,1.56,0.64,1) both !important;
}

/* ── ASSISTANT: stays on the LEFT ── */
[data-testid="stChatMessage"][aria-label*="assistant"] {
    justify-content: flex-start !important;
}
[data-testid="stChatMessage"][aria-label*="assistant"] > div {
    background: transparent !important;
    border: none !important;
    border-radius: 4px 18px 18px 18px !important;
    padding: 0.1rem 0 !important;
    max-width: 78% !important;
    box-shadow: none !important;
    animation: msg-in-left 0.25s cubic-bezier(0.34,1.56,0.64,1) both !important;
}

/* Hide avatars so it's clean like ChatGPT */
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    display: none !important;
}

/* Message text */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {
    font-size: 0.97rem !important;
    line-height: 1.75 !important;
    color: var(--text) !important;
    font-weight: 400 !important;
    margin: 0 0 0.3rem 0 !important;
}
[data-testid="stChatMessage"] p:last-child { margin-bottom: 0 !important; }

/* Code */
[data-testid="stChatMessage"] code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.84rem !important;
    background: #1A1A1A !important;
    border: 1px solid var(--border2) !important;
    padding: 2px 6px !important;
    border-radius: 5px !important;
    color: var(--accent) !important;
}
[data-testid="stChatMessage"] pre {
    background: #1A1A1A !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    padding: 1rem !important;
    font-size: 0.84rem !important;
    overflow-x: auto !important;
}

/* Slide-in animations */
@keyframes msg-in-right {
    from { opacity:0; transform: translateX(14px) scale(0.97); }
    to   { opacity:1; transform: translateX(0)    scale(1);    }
}
@keyframes msg-in-left {
    from { opacity:0; transform: translateX(-14px) scale(0.97); }
    to   { opacity:1; transform: translateX(0)     scale(1);    }
}

/* ══════════════════════════════════════════
   CHAT INPUT  (ChatGPT style — wide pill)
══════════════════════════════════════════ */
[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: min(800px, 94vw) !important;
    padding: 0.8rem 1rem 1.1rem !important;
    background: linear-gradient(to top, var(--bg) 70%, transparent) !important;
    z-index: 999 !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 14px !important;
    padding: 0.85rem 1.1rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.97rem !important;
    color: var(--text) !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    resize: none !important;
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInput"] input::placeholder {
    color: var(--text-muted) !important;
}
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] input:focus {
    border-color: var(--border2) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5),
                0 0 0 2px rgba(91,155,248,0.15) !important;
    outline: none !important;
}
[data-testid="stChatInput"] button {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 9px !important;
    color: #000 !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(91,155,248,0.3) !important;
    transition: all 0.15s !important;
}
[data-testid="stChatInput"] button:hover {
    background: #78B4FF !important;
    transform: scale(1.05) !important;
}

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div {
    padding: 1.6rem 1.2rem !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    border-bottom: 1px solid var(--border) !important;
    padding-bottom: 0.6rem !important;
    margin-bottom: 0.9rem !important;
}

/* ── Radio — CAPS + bigger font ── */
[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
}
[data-testid="stRadio"] label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;          /* bigger */
    font-weight: 600 !important;            /* bolder */
    text-transform: uppercase !important;   /* CAPS */
    letter-spacing: 0.06em !important;
    color: var(--text-soft) !important;
    padding: 0.6rem 0.9rem !important;
    border-radius: var(--r-sm) !important;
    border: 1px solid transparent !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
}
[data-testid="stRadio"] label:hover {
    background: #2A2A2A !important;
    color: var(--text) !important;
    border-color: var(--border2) !important;
}

/* ══════════════════════════════════════════
   MODEL CARD
══════════════════════════════════════════ */
.model-card {
    margin-top: 0.9rem;
    padding: 0.85rem 1rem;
    background: #1C1C1C;
    border: 1px solid var(--border);
    border-radius: var(--r-sm);
    font-size: 0.82rem;
    color: var(--text-muted);
    line-height: 1.6;
}
.model-card .model-name {
    font-size: 0.92rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 5px;
    font-family: 'Syne', sans-serif;
    letter-spacing: -0.01em;
}
.model-card .model-tag {
    display: inline-block;
    font-size: 0.67rem;
    font-family: 'JetBrains Mono', monospace;
    background: var(--accent-p);
    color: var(--accent);
    border: 1px solid rgba(91,155,248,0.25);
    padding: 2px 9px;
    border-radius: var(--r-pill);
    margin-bottom: 7px;
    letter-spacing: 0.05em;
    font-weight: 600;
    text-transform: uppercase;
}
.model-card .warn-tag {
    display: inline-block;
    font-size: 0.67rem;
    font-family: 'JetBrains Mono', monospace;
    background: var(--amber-p);
    color: var(--amber);
    border: 1px solid rgba(251,191,36,0.3);
    padding: 2px 9px;
    border-radius: var(--r-pill);
    margin-bottom: 7px;
    letter-spacing: 0.05em;
    font-weight: 600;
}

/* ══════════════════════════════════════════
   TOKEN METER
══════════════════════════════════════════ */
.token-meter-wrap { margin-top: 1.2rem; }
.token-meter-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 6px;
}
.token-meter-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    font-family: 'JetBrains Mono', monospace;
}
.token-meter-count {
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    font-variant-numeric: tabular-nums;
}
.token-meter-track {
    width: 100%;
    height: 5px;
    background: #2A2A2A;
    border-radius: 99px;
    overflow: hidden;
    border: 1px solid var(--border);
}
.token-meter-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
    position: relative;
    overflow: hidden;
}
/* animated shimmer on the fill bar */
.token-meter-fill::after {
    content: '';
    position: absolute;
    top: 0; left: -60%; width: 50%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    animation: shimmer 2.2s ease-in-out infinite;
}
@keyframes shimmer {
    0%   { left: -60%; }
    100% { left: 120%; }
}
.token-meter-fill.ok      { background: linear-gradient(90deg,#34D399,#6EE7B7); }
.token-meter-fill.warning { background: linear-gradient(90deg,#FBBF24,#FCD34D); }
.token-meter-fill.danger  { background: linear-gradient(90deg,#F87171,#FCA5A5); }
.token-meter-sub {
    margin-top: 4px;
    font-size: 0.68rem;
    color: var(--text-dim);
    font-family: 'JetBrains Mono', monospace;
    text-align: right;
}

/* ══════════════════════════════════════════
   AUTO-SWITCH BANNER
══════════════════════════════════════════ */
.switch-banner {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 0.9rem 1.1rem;
    background: rgba(251,191,36,0.07);
    border: 1px solid rgba(251,191,36,0.18);
    border-left: 3px solid var(--amber);
    border-radius: var(--r-sm);
    margin-bottom: 1.2rem;
    animation: fadein 0.3s ease;
}
.switch-banner .icon { font-size: 1rem; flex-shrink: 0; margin-top: 2px; }
.switch-banner .text { font-size: 0.84rem; line-height: 1.6; color: #B8912A; }
.switch-banner .text strong {
    font-weight: 700; display: block;
    margin-bottom: 2px; color: var(--amber);
}
@keyframes fadein {
    from { opacity:0; transform:translateY(-6px); }
    to   { opacity:1; transform:translateY(0); }
}

/* ══════════════════════════════════════════
   SIDEBAR CLEAR BUTTON
══════════════════════════════════════════ */
[data-testid="stSidebar"] button {
    background: #1C1C1C !important;
    border: 1px solid var(--border2) !important;
    color: var(--text-muted) !important;
    border-radius: var(--r-sm) !important;
    font-size: 0.88rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.18s ease !important;
}
[data-testid="stSidebar"] button:hover {
    background: var(--red-p) !important;
    border-color: var(--red) !important;
    color: var(--red) !important;
}

/* ══════════════════════════════════════════
   BUFFERING / TYPING ANIMATION
══════════════════════════════════════════ */
/* Animated typing dots — ChatGPT style */
.typing-indicator {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 0.6rem 0.2rem;
}
.typing-indicator span {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--text-muted);
    display: inline-block;
    animation: typing-bounce 1.3s ease-in-out infinite;
}
.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-bounce {
    0%, 60%, 100% { transform: translateY(0);    opacity: 0.4; }
    30%            { transform: translateY(-7px); opacity: 1;   }
}

/* Processing pulse ring around bot icon */
@keyframes pulse-ring {
    0%   { box-shadow: 0 0 0 0 rgba(91,155,248,0.4); }
    70%  { box-shadow: 0 0 0 8px rgba(91,155,248,0); }
    100% { box-shadow: 0 0 0 0 rgba(91,155,248,0); }
}
.processing .bot-icon {
    animation: pulse-ring 1.2s ease-out infinite !important;
}

/* Spinner override */
.stSpinner > div {
    border-top-color: var(--accent) !important;
    border-right-color: rgba(91,155,248,0.12) !important;
    border-bottom-color: rgba(91,155,248,0.12) !important;
    border-left-color: rgba(91,155,248,0.12) !important;
    width: 20px !important;
    height: 20px !important;
}

/* ══════════════════════════════════════════
   EMPTY STATE
══════════════════════════════════════════ */
.empty-state {
    text-align: center;
    padding: 5rem 1rem 3rem;
}
.empty-state .icon {
    font-size: 3rem;
    margin-bottom: 1.2rem;
    display: block;
    opacity: 0.18;
}
.empty-state .title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text);
    font-family: 'Syne', sans-serif;
    letter-spacing: -0.02em;
    margin-bottom: 0.5rem;
}
.empty-state .sub {
    font-size: 0.9rem;
    color: var(--text-muted);
    line-height: 1.65;
    max-width: 320px;
    margin: 0 auto;
}
.empty-state .hint {
    margin-top: 1.6rem;
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-dim);
    letter-spacing: 0.05em;
}

/* Suggestion chips */
.chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-top: 1.4rem;
}
.chip {
    font-size: 0.82rem;
    color: var(--text-soft);
    background: #2A2A2A;
    border: 1px solid var(--border2);
    border-radius: 99px;
    padding: 6px 16px;
    cursor: default;
    transition: all 0.15s;
    font-family: 'Inter', sans-serif;
}
.chip:hover {
    background: #333;
    border-color: var(--accent);
    color: var(--accent);
}

/* ══════════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════════ */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #3A3A3A; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #555; }

/* ══════════════════════════════════════════
   DIVIDER
══════════════════════════════════════════ */
.hr {
    height: 1px;
    background: var(--border);
    margin: 1.2rem 0;
}
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
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False


# ── Token bar ──────────────────────────────────────────────────────────────────
def _token_bar_html(used: int, limit: int) -> str:
    pct = min(used / limit * 100, 100) if limit else 0
    if pct < 60:
        state, color = "ok", "#34D399"
    elif pct < 85:
        state, color = "warning", "#FBBF24"
    else:
        state, color = "danger", "#F87171"
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
    tag_text  = "⚠ limit reached — switched" if locked else provider

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

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    if st.button("🗑  Clear conversation", use_container_width=True):
        reset_session(st.session_state.session_id)
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.groq_tokens_used = 0
        st.session_state.show_switch_banner = False
        st.session_state.model_choice = "chatgroq"
        st.session_state.is_processing = False
        st.rerun()


# ── Page header ────────────────────────────────────────────────────────────────
processing_class = "processing" if st.session_state.is_processing else ""
st.markdown(f"""
<div class="page-header {processing_class}">
    <div class="left">
        <div class="bot-icon">🤖</div>
        <h1>Unified Chatbot</h1>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
        <span class="status-dot"></span>
        <span class="model-pill">{model_choice}</span>
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
            Now on Gemma 3 locally — free &amp; unlimited.
            Clear conversation to reset quota.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Empty state ────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <span class="icon">🤖</span>
        <div class="title">How can I help you today?</div>
        <div class="sub">Switch between Groq (cloud) and Ollama (local) from the sidebar.</div>
        <div class="chips">
            <span class="chip">Explain a concept</span>
            <span class="chip">Write some code</span>
            <span class="chip">Summarize text</span>
            <span class="chip">Answer a question</span>
        </div>
        <div class="hint">↓ &nbsp; type below to start</div>
    </div>
    """, unsafe_allow_html=True)

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Input & response ───────────────────────────────────────────────────────────
user_input = st.chat_input("Message Unified Chatbot…")

if user_input:
    st.session_state.is_processing = True
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        # ChatGPT-style animated typing indicator while processing
        typing_ph = st.empty()
        typing_ph.markdown("""
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
        """, unsafe_allow_html=True)

        result = get_answer(
            user_input,
            model_choice,
            st.session_state.session_id,
        )

        # Replace dots with actual response
        typing_ph.empty()
        st.markdown(result.response)

    st.session_state.is_processing = False
    st.session_state.groq_tokens_used = result.groq_tokens_total

    if result.auto_switched and not st.session_state.show_switch_banner:
        st.session_state.show_switch_banner = True
        st.session_state.model_choice = "ollama"

    st.session_state.messages.append({"role": "assistant", "content": result.response})
    st.rerun()