import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, File, UploadFile, status, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv

import llm
from main import process_and_store_pdf
# Make sure this matches whatever you named the advanced JSON evaluator in evaluator.py
from evaluator import evaluate_faithfulness 

app = FastAPI(title="FinDoc", description="Query document using RAG")

# Setup upload directory
UPLOAD_DIR = Path("uploaded_pdfs")
UPLOAD_DIR.mkdir(exist_ok=True)

# --- Pydantic Models ---
class questionRequest(BaseModel):
    question: str

class HealthResponse(BaseModel):
    status: str

# Flattened to match Streamlit's expectations perfectly
class answer_response(BaseModel):
    answer: str
    status: str
    reasoning: str


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok"}


@app.post("/upload-pdf/")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # 1. Create the physical file path
    file_path = UPLOAD_DIR / file.filename
    
    # 2. ACTUALLY SAVE THE FILE TO DISK
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
    finally:
        await file.close()
    
    # 3. Hand off the saved path to the background worker
    background_tasks.add_task(process_and_store_pdf, str(file_path))
    
    return {"message": "File uploaded successfully. Processing has started in the background."}


@app.post("/ask", response_model=answer_response)
def ask_question(ques: questionRequest):
    try:
        user_question = ques.question
        
        # 1. Get the answer and the context from your RAG pipeline
        ai_answer, retrieved_context = llm.llm_response(user_question)
        
        # 2. Run the evaluator (which now returns a dictionary)
        eval_result = evaluate_faithfulness(retrieved_context, ai_answer)
        
        # 3. Return the flat structure
        return {
            "answer": ai_answer,
            "status": eval_result.get("status", "FAILED"),
            "reasoning": eval_result.get("reasoning", "No reasoning returned.")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")