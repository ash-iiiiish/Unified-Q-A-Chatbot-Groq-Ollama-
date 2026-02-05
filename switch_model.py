from chatgroq_model import get_chatgroq_answer
from ollama_model import get_ollama_answer

def get_answer(question: str, model_type: str, session_id: str):
    if model_type == "chatgroq":
        return get_chatgroq_answer(question, session_id)
    elif model_type == "ollama":
        return get_ollama_answer(question, session_id)
    else:
        return "Invalid model selected"
