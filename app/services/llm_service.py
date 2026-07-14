from app.config.settings import settings

from langchain_groq import ChatGroq

from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm():

    if settings.LLM_PROVIDER == "groq":

        return ChatGroq(
            model=settings.DEFAULT_MODEL,
            api_key=settings.GROQ_API_KEY
        )

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.GOOGLE_API_KEY
    )