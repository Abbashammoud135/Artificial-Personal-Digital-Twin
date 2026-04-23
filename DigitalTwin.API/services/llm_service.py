from langchain_community.llms import Ollama

llm = Ollama(model="llama3")

def run_llm(prompt: str):
    return llm.invoke(prompt)