from langchain_openai import ChatOpenAI, AzureChatOpenAI
from qa_agent.config.settings import settings

def get_llm(temperature: float = 0):
    """
    Returns the configured LLM Instance (OpenAI or Azure).
    """
    if settings.llm.provider.lower() == "azure":
        if not settings.llm.api_key or not settings.llm.azure_endpoint:
            print("WARNING: Azure credentials missing. Check AZURE_OPENAI_ENDPOINT and OPENAI_API_KEY.")
            
        return AzureChatOpenAI(
            azure_endpoint=settings.llm.azure_endpoint,
            openai_api_version=settings.llm.azure_api_version,
            azure_deployment=settings.llm.azure_deployment,
            api_key=settings.llm.api_key,
            temperature=temperature,
        )
    else:
        if not settings.llm.api_key:
            print("WARNING: OPENAI_API_KEY is missing.")
            
        return ChatOpenAI(
            model=settings.llm.model_name,
            api_key=settings.llm.api_key,
            temperature=temperature,
        )
