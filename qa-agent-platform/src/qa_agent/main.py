import typer
import sys
# Safeguard for Library-Level Import Errors in certain Python/LangChain environments
try:
    from langchain_core.language_models.base import BaseLanguageModel
    from langchain_core.prompts.chat import ChatPromptTemplate
except ImportError:
    pass

from qa_agent.cli.app import app

if __name__ == "__main__":
    app()
