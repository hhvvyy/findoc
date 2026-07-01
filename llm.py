import os
from dotenv import load_dotenv
from vector_store import query_database
from groq import Groq

load_dotenv()

# 1 initialize the Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def llm_response(question: str):
    
    # send the question to vector_store.py and get the context back
    context_string = query_database(question)

    # 2. sending the data to Groq
    chat_completion = client.chat.completions.create(
        messages=[
            # 🧠 ADDED SYSTEM PROMPT: Forces the LLM to provide factual, direct answers without meta-filler
            {
                "role": "system",
                "content": """
You are an equity research analyst.

Use ONLY the supplied context.

You may perform logical reasoning and combine facts from multiple sections.

You may infer conclusions ONLY when they are directly supported by multiple facts in the document.

Never invent facts.

Never use outside knowledge.

When making an inference, explicitly state:

"Evidence suggests..."

or

"The report indicates..."

If evidence is insufficient, state that.
"""
            },
            {
                "role": "user",
                "content": f"Answer to question '{question}' using the following retrieved context:\n\n{context_string}",
            }
        ],
        model="llama-3.3-70b-versatile", 
    )

    # Return the direct answer and the raw text chunks
    return chat_completion.choices[0].message.content, context_string