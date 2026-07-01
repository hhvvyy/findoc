# app.py
import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, File, UploadFile, status, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv

import llm
from main import process_and_store_pdf
from evaluator import evaluate_faithfulness

app = FastAPI(title="findoc", description="query document using RAG")

# Setup upload directory
UPLOAD_DIR = Path("uploaded_pdfs")
UPLOAD_DIR.mkdir(exist_ok=True)

# Pydantic models
class questionRequest(BaseModel):
    question: str

class answer_response(BaseModel):
    answer: str

class HealthResponse(BaseModel):
    status: str

class answer_response(BaseModel):
    answer:str
    status:str


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
        ai_answer,retrived_context = llm.llm_response(user_question)
        eval_status=evaluate_faithfulness(retrived_context,ai_answer)
        return {
            "answer": ai_answer,
            "status":eval_status
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")