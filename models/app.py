import streamlit as st
import uuid
import html as html_lib
from switch_model import get_answer, reset_session, GROQ_SESSION_TOKEN_LIMIT

st.set_page_config(
    page_title="Unified Chatbot",
    page_icon="🤖",
    layout="centered",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Syne:wght@600;700;800&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg:           #212121;
    --bg-sidebar:   #171717;
    --bg-input:     #2F2F2F;
    --border:       #3A3A3A;
    --border2:      #484848;
    --text:         #ECECEC;
    --text-soft:    #B4B4B4;
    --text-muted:   #787878;
    --text-dim:     #4A4A4A;
    --accent:       #5B9BF8;
    --accent-p:     rgba(91,155,248,0.08);
    --green:        #3DDC97;
    --green-g:      rgba(61,220,151,0.3);
    --amber:        #FBBF24;
    --amber-p:      rgba(251,191,36,0.10);
    --red:          #F87171;
    --red-p:        rgba(248,113,113,0.10);

    /* WhatsApp-style bubble colors */
    --bubble-user:  #005C4B;   /* WhatsApp dark green for sent */
    --bubble-bot:   #1E2D3D;   /* Dark blue-gray for received  */
    --bubble-user-border: #007A63;
    --bubble-bot-border:  #2A3F55;

    --r-sm:   10px;
    --r-pill: 999px;
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
    font-size: 16px !important;
}
.stApp { background: var(--bg) !important; }
.main .block-container {
    max-width: 1100px !important;
    width: 100% !important;
}
header[data-testid="stHeader"] { background: transparent !important; }

/* ── Wipe default Streamlit chat chrome ── */
[data-testid="stChatMessage"],
[data-testid="stChatMessage"] > div {
    all: unset !important;
    display: block !important;
}
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"],
[data-testid="stChatMessageAvatar"] { display: none !important; }

/* ══════════════════════════════════════════
   CHAT CONTAINER — one HTML block
══════════════════════════════════════════ */
.chat-window {
    display: flex;
    flex-direction: column;
    gap: 12px;
    width: 100%;
    max-width: 100%;
}
/* ── Each row ── */
.chat-row {
    display: flex;
    width: 100%;
    align-items: flex-end;
    gap: 8px;
    min-width: 60px;
}

/* YOUR message → RIGHT */
.chat-row.user-row {
    justify-content: flex-end;
}

/* AI message → LEFT */
.chat-row.bot-row {
    flex-direction: row;
    justify-content: flex-start;
}

/* ── Mini avatar circle ── */
.avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 700;
}
.avatar-user {
    background: #005C4B;
    color: #fff;
    border: 1px solid #007A63;
}
.avatar-bot {
    background: #1C2D3E;
    color: #5B9BF8;
    border: 1px solid #2A3F55;
    font-size: 1rem;
}

/* ── Bubble ── */
.bubble {
    max-width: 68%;
    min-width: 120px;          /* prevents collapsing */
    padding: 0.72rem 1rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    line-height: 1.68;

    white-space: normal;       /* allow normal wrapping */
    word-break: normal;        /* stop breaking every letter */
    overflow-wrap: break-word; /* wrap long words only */

    position: relative;
}

/* USER bubble — WhatsApp dark green, RIGHT, tail bottom-right */
.bubble-user {
    background: var(--bubble-user);
    border: 1px solid var(--bubble-user-border);
    color: #E9F5F3;
    border-radius: 16px 16px 2px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    animation: pop-right 0.22s cubic-bezier(0.34,1.5,0.64,1) both;
}

/* BOT bubble — dark blue-gray, LEFT, tail bottom-left */
.bubble-bot {
    background: var(--bubble-bot);
    border: 1px solid var(--bubble-bot-border);
    color: var(--text);
    border-radius: 16px 16px 16px 2px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    animation: pop-left 0.22s cubic-bezier(0.34,1.5,0.64,1) both;
}

/* Timestamp-style label under bubble */
.bubble-meta {
    font-size: 0.65rem;
    font-family: 'JetBrains Mono', monospace;
    color: rgba(255,255,255,0.35);
    margin-top: 4px;
    text-align: right;
}
.bot-row .bubble-meta { text-align: left; }

/* Slide animations */
@keyframes pop-right {
    from { opacity:0; transform: translateX(18px) scale(0.95); }
    to   { opacity:1; transform: translateX(0)    scale(1);    }
}
@keyframes pop-left {
    from { opacity:0; transform: translateX(-18px) scale(0.95); }
    to   { opacity:1; transform: translateX(0)     scale(1);    }
}

/* ══════════════════════════════════════════
   TYPING INDICATOR  (left side, bot)
══════════════════════════════════════════ */
.typing-wrap {
    display: flex;
    align-items: flex-end;
    gap: 8px;
    padding: 0.3rem 0;
}
.typing-bubble {
    background: var(--bubble-bot);
    border: 1px solid var(--bubble-bot-border);
    border-radius: 16px 16px 16px 2px;
    padding: 0.7rem 1rem;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}
.typing-bubble span {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--text-muted);
    animation: bounce 1.3s ease-in-out infinite;
}
.typing-bubble span:nth-child(2) { animation-delay: 0.2s; }
.typing-bubble span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%,60%,100% { transform:translateY(0);    opacity:0.35; }
    30%          { transform:translateY(-7px); opacity:1; }
}

/* ══════════════════════════════════════════
   PAGE HEADER
══════════════════════════════════════════ */
.page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 0;
    margin-bottom: 1.2rem;
    border-bottom: 1px solid var(--border);
}
.page-header .left { display:flex; align-items:center; gap:10px; }
.page-header .bot-icon {
    width:36px; height:36px; border-radius:8px;
    background:#2A2A2A; border:1px solid var(--border2);
    display:flex; align-items:center; justify-content:center; font-size:1.1rem;
}
.page-header h1 {
    font-family:'Syne',sans-serif !important;
    font-size:1.12rem !important; font-weight:700 !important;
    color:var(--text) !important; margin:0 !important;
}
.model-pill {
    font-family:'JetBrains Mono',monospace; font-size:0.67rem;
    font-weight:600; letter-spacing:0.07em; text-transform:uppercase;
    color:var(--accent); background:var(--accent-p);
    border:1px solid rgba(91,155,248,0.25);
    padding:3px 10px; border-radius:var(--r-pill);
}
.status-dot {
    width:7px; height:7px; border-radius:50%;
    background:var(--green); box-shadow:0 0 8px var(--green-g);
    display:inline-block; animation:blink 2.5s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ══════════════════════════════════════════
   CHAT INPUT — centered in content area
══════════════════════════════════════════ */
[data-testid="stChatInput"] {
    position: fixed !important;
    left: calc(50% + 150px) !important;  /* compensate sidebar */
    transform: translateX(-50%) !important;
    bottom: 24px !important;

    width: min(900px, 90%) !important;
    max-width: 900px !important;

    padding: 0 !important;
    background: transparent !important;
    z-index: 999 !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 14px !important;
    padding: 0.88rem 1.2rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.97rem !important;
    color: var(--text) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInput"] input::placeholder { color:var(--text-muted) !important; }
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] input:focus {
    border-color: var(--border2) !important;
    box-shadow: 0 4px 28px rgba(0,0,0,0.55), 0 0 0 2px rgba(91,155,248,0.18) !important;
    outline: none !important;
}
[data-testid="stChatInput"] button {
    background: var(--accent) !important; border:none !important;
    border-radius: 9px !important; color:#fff !important;
    font-weight:700 !important;
    box-shadow: 0 2px 8px rgba(91,155,248,0.35) !important;
    transition: all 0.15s !important;
}
[data-testid="stChatInput"] button:hover {
    background: #78B4FF !important; transform: scale(1.06) !important;
}

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div { padding:1.6rem 1.2rem !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family:'JetBrains Mono',monospace !important; font-size:0.68rem !important;
    font-weight:600 !important; letter-spacing:0.14em !important;
    text-transform:uppercase !important; color:var(--text-muted) !important;
    border-bottom:1px solid var(--border) !important;
    padding-bottom:0.6rem !important; margin-bottom:0.9rem !important;
}
[data-testid="stRadio"] > div { display:flex !important; flex-direction:column !important; gap:4px !important; }
[data-testid="stRadio"] label {
    font-family:'Inter',sans-serif !important; font-size:0.95rem !important;
    font-weight:600 !important; text-transform:uppercase !important;
    letter-spacing:0.06em !important; color:var(--text-soft) !important;
    padding:0.6rem 0.9rem !important; border-radius:var(--r-sm) !important;
    border:1px solid transparent !important; cursor:pointer !important; transition:all 0.15s !important;
}
[data-testid="stRadio"] label:hover {
    background:#2A2A2A !important; color:var(--text) !important; border-color:var(--border2) !important;
}

/* Model card */
.model-card {
    margin-top:0.9rem; padding:0.85rem 1rem;
    background:#1C1C1C; border:1px solid var(--border); border-radius:var(--r-sm);
    font-size:0.82rem; color:var(--text-muted); line-height:1.6;
}
.model-card .model-name { font-size:0.9rem; font-weight:700; color:var(--text); margin-bottom:5px; font-family:'Syne',sans-serif; }
.model-card .model-tag {
    display:inline-block; font-size:0.67rem; font-family:'JetBrains Mono',monospace;
    background:var(--accent-p); color:var(--accent); border:1px solid rgba(91,155,248,0.25);
    padding:2px 9px; border-radius:var(--r-pill); margin-bottom:7px;
    letter-spacing:0.05em; font-weight:600; text-transform:uppercase;
}
.model-card .warn-tag {
    display:inline-block; font-size:0.67rem; font-family:'JetBrains Mono',monospace;
    background:var(--amber-p); color:var(--amber); border:1px solid rgba(251,191,36,0.3);
    padding:2px 9px; border-radius:var(--r-pill); margin-bottom:7px; letter-spacing:0.05em; font-weight:600;
}

/* Token meter */
.token-meter-wrap { margin-top:1.2rem; }
.token-meter-header { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:6px; }
.token-meter-label { font-size:0.68rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:var(--text-muted); font-family:'JetBrains Mono',monospace; }
.token-meter-count { font-size:0.72rem; font-weight:600; font-family:'JetBrains Mono',monospace; font-variant-numeric:tabular-nums; }
.token-meter-track { width:100%; height:5px; background:#2A2A2A; border-radius:99px; overflow:hidden; border:1px solid var(--border); }
.token-meter-fill { height:100%; border-radius:99px; transition:width 0.5s cubic-bezier(0.4,0,0.2,1); position:relative; overflow:hidden; }
.token-meter-fill::after { content:''; position:absolute; top:0; left:-60%; width:50%; height:100%; background:linear-gradient(90deg,transparent,rgba(255,255,255,0.25),transparent); animation:shimmer 2.5s ease-in-out infinite; }
@keyframes shimmer { 0%{left:-60%} 100%{left:120%} }
.token-meter-fill.ok      { background:linear-gradient(90deg,#34D399,#6EE7B7); }
.token-meter-fill.warning { background:linear-gradient(90deg,#FBBF24,#FCD34D); }
.token-meter-fill.danger  { background:linear-gradient(90deg,#F87171,#FCA5A5); }
.token-meter-sub { margin-top:4px; font-size:0.68rem; color:var(--text-dim); font-family:'JetBrains Mono',monospace; text-align:right; }

/* Auto-switch banner */
.switch-banner {
    display:flex; align-items:flex-start; gap:10px;
    padding:0.9rem 1.1rem; background:rgba(251,191,36,0.07);
    border:1px solid rgba(251,191,36,0.18); border-left:3px solid var(--amber);
    border-radius:var(--r-sm); margin-bottom:1.2rem; animation:fadein 0.3s ease;
}
.switch-banner .icon { font-size:1rem; flex-shrink:0; margin-top:2px; }
.switch-banner .text { font-size:0.84rem; line-height:1.6; color:#B8912A; }
.switch-banner .text strong { font-weight:700; display:block; margin-bottom:2px; color:var(--amber); }
@keyframes fadein { from{opacity:0;transform:translateY(-6px)} to{opacity:1;transform:translateY(0)} }

/* Clear button */
[data-testid="stSidebar"] button {
    background:#1C1C1C !important; border:1px solid var(--border2) !important;
    color:var(--text-muted) !important; border-radius:var(--r-sm) !important;
    font-size:0.88rem !important; font-family:'Inter',sans-serif !important;
    font-weight:500 !important; transition:all 0.18s ease !important;
}
[data-testid="stSidebar"] button:hover {
    background:var(--red-p) !important; border-color:var(--red) !important; color:var(--red) !important;
}

/* Empty state */
.empty-state { text-align:center; padding:5rem 1rem 3rem; }
.empty-state .icon { font-size:3rem; margin-bottom:1.2rem; display:block; opacity:0.18; }
.empty-state .title { font-size:1.5rem; font-weight:700; color:var(--text); font-family:'Syne',sans-serif; letter-spacing:-0.02em; margin-bottom:0.5rem; }
.empty-state .sub { font-size:0.9rem; color:var(--text-muted); line-height:1.65; max-width:320px; margin:0 auto; }
.chips { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin-top:1.4rem; }
.chip { font-size:0.82rem; color:var(--text-soft); background:#2A2A2A; border:1px solid var(--border2); border-radius:99px; padding:6px 16px; font-family:'Inter',sans-serif; }
.empty-state .hint { margin-top:1.6rem; font-size:0.72rem; font-family:'JetBrains Mono',monospace; color:var(--text-dim); letter-spacing:0.05em; }

::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#3A3A3A; border-radius:4px; }
.hr { height:1px; background:var(--border); margin:1.2rem 0; }
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


# ── Build ENTIRE chat window as one HTML block ─────────────────────────────────
def build_chat_html(messages: list, typing: bool = False) -> str:
    """
    Renders all messages + optional typing indicator as a SINGLE HTML string.
    One st.markdown() call = one DOM element = flex layout works perfectly.
    """
    rows = []
    for msg in messages:
        safe = html_lib.escape(msg["content"]).replace("\n", "<br>")
        if msg["role"] == "user":
            rows.append(f"""
            <div class="chat-row user-row">
                <div>
                    <div class="bubble bubble-user">{safe}</div>
                    <div class="bubble-meta">You</div>
                </div>
                <div class="avatar avatar-user">Y</div>
            </div>""")
        else:
            rows.append(f"""
            <div class="chat-row bot-row">
                <div class="avatar avatar-bot">🤖</div>
                <div>
                    <div class="bubble bubble-bot">{safe}</div>
                    <div class="bubble-meta">Assistant</div>
                </div>
            </div>""")

    if typing:
        rows.append("""
        <div class="typing-wrap">
            <div class="avatar avatar-bot">🤖</div>
            <div class="typing-bubble">
                <span></span><span></span><span></span>
            </div>
        </div>""")

    return f'<div class="chat-window">{"".join(rows)}</div>'


# ── Token bar ──────────────────────────────────────────────────────────────────
def _token_bar_html(used: int, limit: int) -> str:
    pct = min(used / limit * 100, 100) if limit else 0
    state = "ok" if pct < 60 else ("warning" if pct < 85 else "danger")
    color = "#34D399" if pct < 60 else ("#FBBF24" if pct < 85 else "#F87171")
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
    </div>"""


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Model")

    locked = st.session_state.groq_tokens_used >= GROQ_SESSION_TOKEN_LIMIT
    radio_index = 1 if locked else (0 if st.session_state.model_choice == "chatgroq" else 1)

    model_choice = st.radio(
        "model", ["chatgroq", "ollama"],
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
    </div>""", unsafe_allow_html=True)

    st.markdown(_token_bar_html(
        st.session_state.groq_tokens_used, GROQ_SESSION_TOKEN_LIMIT,
    ), unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

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
            Clear conversation to reset.
        </div>
    </div>""", unsafe_allow_html=True)

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
    </div>""", unsafe_allow_html=True)

# ── Chat window placeholder (one slot, always updated) ────────────────────────
chat_slot = st.empty()

# Render current history (no typing indicator)
if st.session_state.messages:
    chat_slot.markdown(
        build_chat_html(st.session_state.messages, typing=False),
        unsafe_allow_html=True,
    )

# ── Input ──────────────────────────────────────────────────────────────────────
user_input = st.chat_input("Message Unified Chatbot…")

if user_input:
    # 1. Add user message and show with typing dots
    st.session_state.messages.append({"role": "user", "content": user_input})
    chat_slot.markdown(
        build_chat_html(st.session_state.messages, typing=True),
        unsafe_allow_html=True,
    )

    # 2. Call model
    result = get_answer(user_input, model_choice, st.session_state.session_id)

    # 3. Add response, remove typing dots
    st.session_state.messages.append({"role": "assistant", "content": result.response})
    st.session_state.groq_tokens_used = result.groq_tokens_total

    if result.auto_switched and not st.session_state.show_switch_banner:
        st.session_state.show_switch_banner = True
        st.session_state.model_choice = "ollama"

    # 4. Rerun to refresh sidebar meter + banner
    st.rerun()