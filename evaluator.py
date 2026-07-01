# evaluator.py
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
# Initialize the client just like in llm.py
client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def evaluate_faithfulness(context: str, answer: str) -> str:
    """
    Asks a judge LLM to verify if the answer is grounded completely in the context.
    """
    
    # The secret sauce is a highly structured system prompt
    system_instruction = (
        


    "You are a strict compliance auditor checking if an AI assistant's answer is faithful to the provided context.\n\n"
    "CRITICAL RULES:\n"
    "1. If the assistant explicitly states that the information is NOT present, cannot be found, "
    "or that it does not know the answer, you MUST evaluate this as 'PASSED'. Refusing to hallucinate is correct behavior.\n"
    "2. If the assistant provides facts, numbers, or metrics, check if they are directly supported by the context. "
    "If any metric or number is completely missing or altered, respond with 'FAILED'.\n\n"
    "Respond with exactly one word: either 'PASSED' or 'FAILED'."
)
    
    
    user_payload = f"CONTEXT:\n{context}\n\nANSWER:\n{answer}"
    
    # Call a fast, smart model to do the judging
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_payload}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.0, # CRITICAL: Keep temperature at 0 for strict, deterministic grading
    )
    
    return response.choices[0].message.content.strip()