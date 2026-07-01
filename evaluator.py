import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def evaluate_faithfulness(context: str, answer: str) -> dict:
    """
    Advanced judge LLM that uses Chain-of-Thought to verify faithfulness 
    and returns a structured JSON response.
    """
    
    system_instruction = (
        "You are an expert compliance auditor evaluating an AI assistant's answer for 'faithfulness' to a provided context. "
        "Your task is to ensure the answer does not contain any hallucinations or unsupported claims.\n\n"
        
        "CRITICAL RULES:\n"
        "1. REFUSALS: If the assistant explicitly states it does not know, cannot find the info, or refuses to guess, "
        "evaluate this as 'PASSED'. Refusing to hallucinate is exactly what we want.\n"
        "2. METRICS & FACTS: If the assistant provides facts, numbers, or entities, every single one must be explicitly "
        "supported by the context. If even one metric is hallucinated or altered, the status is 'FAILED'.\n"
        "3. DEDUCTIONS: The assistant is allowed to make logical deductions if they are direct, obvious consequences of the context.\n\n"
        
        "EVALUATION STEPS (Perform these in your reasoning):\n"
        "Step 1: Extract all factual claims made in the ANSWER.\n"
        "Step 2: Cross-check each extracted claim against the CONTEXT to see if it is explicitly supported.\n"
        "Step 3: Determine the final verdict ('PASSED' or 'FAILED').\n\n"
        
        "OUTPUT FORMAT:\n"
        "You MUST return a valid JSON object with exactly two keys:\n"
        "- \"reasoning\": A string containing your step-by-step logic and claim cross-checking.\n"
        "- \"status\": A string strictly containing either \"PASSED\" or \"FAILED\"."
    )
    
    user_payload = f"CONTEXT:\n{context}\n\nANSWER:\n{answer}"
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_payload}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.0, 
            response_format={"type": "json_object"}, # CRITICAL: Forces strict JSON output
        )
        
        # parse the JSON string into a Python dictionary
        result = json.loads(response.choices[0].message.content.strip())
        return result
        
    except Exception as e:
        # fallback for API errors or JSON parsing failures
        return {"reasoning": f"Evaluation failed due to error: {str(e)}", "status": "FAILED"}

# --- Example usage ---
# result = evaluate_faithfulness_advanced(my_context, my_answer)
# print(f"Verdict: {result['status']}")
# print(f"Why: {result['reasoning']}")