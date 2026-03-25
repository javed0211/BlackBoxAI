import os
from pydantic import BaseModel

class LLMSettings(BaseModel):
    # 'openai' or 'azure'
    provider: str = os.getenv("LLM_PROVIDER", "azure")
    model_name: str = os.getenv("LLM_MODEL_NAME", "gpt-4.1")
    
    # Needs to be set in your terminal or .env
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Azure Specific Parameters
    azure_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "https://rfpqualityai2.cognitiveservices.azure.com/")
    azure_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    azure_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")

class ADOSettings(BaseModel):
    org_url: str = os.getenv("ADO_ORG_URL", "https://dev.azure.com/Organization")
    project: str = os.getenv("ADO_PROJECT", "Project")
    pat: str = os.getenv("ADO_PAT", "")

class JiraSettings(BaseModel):
    host: str = os.getenv("JIRA_HOST", "https://your-domain.atlassian.net")
    email: str = os.getenv("JIRA_EMAIL", "")
    api_token: str = os.getenv("JIRA_API_TOKEN", "")


class Settings(BaseModel):
    llm: LLMSettings = LLMSettings()
    ado: ADOSettings = ADOSettings()
    jira: JiraSettings = JiraSettings()


settings = Settings()
