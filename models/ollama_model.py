from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory


_session_store: dict[str, ChatMessageHistory] = {}


def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in _session_store:
        _session_store[session_id] = ChatMessageHistory()
    return _session_store[session_id]


llm = ChatOllama(
    model="gemma3",
    temperature=0.3,
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


def get_ollama_answer(question: str, session_id: str) -> str:
    return chat_chain.invoke(
        {"question": question},
        config={"configurable": {"session_id": session_id}},
    )