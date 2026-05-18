from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import datetime

llm = ChatOpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1",
    model="llama-3.3-70b-versatile",
    temperature=0.3
)

def test_chain():
    prompt = ChatPromptTemplate.from_template("say hi")

    chain = prompt | llm

    result = chain.invoke({})

    print(result.content)

start = datetime.datetime.now()

test_chain()

mid = datetime.datetime.now()

print("Execution time first:", mid - start)

test_chain()

end = datetime.datetime.now()

print("Execution time second:", end - mid)