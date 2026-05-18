from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
import datetime

# def get_llm():
#     return ChatOllama(
#         model="llama3",
#         temperature=0.3
#     )
# def test_medical_chain():
#     llm = get_llm()

#     prompt = ChatPromptTemplate.from_template("""say hello""")
#     chain = prompt | llm
#     result = chain.invoke({})
#     print(result.content)
from google import genai
import os

_client = None

def get_gemini_client():
    global _client

    if _client is None:
        _client = genai.Client(
            api_key="AIzaSyAg5a9Osxms7DSov-KvTtELpvWwPMSG6YA"
        )

    return _client
client=get_gemini_client()
def test_medical_chain():
    prompt="""say hi"""
    response = client.models.generate_content(   
        model="gemini-3.1-flash-lite-preview",
        contents=prompt
        )
    print(response.text)



time=datetime.datetime.now()
test_medical_chain()
time2=datetime.datetime.now()
print("Execution time first:", time2 - time)
test_medical_chain()
time3=datetime.datetime.now()
print("Execution time second:", time3 - time2)
