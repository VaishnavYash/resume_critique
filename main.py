import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, File, UploadFile, Form, HTTPException

from config import constants
from utils import text_extract_from_pdf as textFormat, utils
from services import openai_services as services

from core import new_resume_agent as resumeAgent, job_description_agent as jdAgent
# uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Load environment variables from .env file
load_dotenv() 

# Initialize FastAPI app
app = FastAPI()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)

client = get_openai_client() 

@app.post("/analyze_resume_pdf")
async def analyze_resume_pdf(
    resume: UploadFile = File(...),
    job_description: str = Form(constants.constJD)
):
    try:
        file_bytes = await resume.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "code": "EMPTY_FILE",
                    "message": "Uploaded file is empty"
                }
            )

        text =  textFormat.extract_text_from_pdf(file_bytes)

        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail={
                    "status": "error",
                    "code": "TEXT_EXTRACTION_FAILED",
                    "message": "No text extracted from PDF",
                    "hint": "PDF might be scanned or image-based"
                }
            )

        # JD Part
        jobAgent = jdAgent.JobDescriptionAgent(llm_client=client)
        job_json = jobAgent.run(job_description)
        
        return services.getAPIResponse(text, job_json, client)

    # Let FastAPI handle it
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "code": "RESUME_PROCESSING_ERROR",
                "message": "Failed to process resume",
                "details": str(e)
            }
        )

@app.post("/get_pdf_data")
async def get_pdf_content(
    job_description: str = Form(constants.constJD),
    resume: UploadFile = File(...)
):
    try:
        file_bytes = await resume.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "code": "EMPTY_FILE",
                    "message": "Uploaded file is empty"
                }
            )
            
        text =  textFormat.extract_text_with_inline_urls(file_bytes)
        
        if not text.strip():
            raise HTTPException(
                status_code=422,
                detail={
                    "status": "error",
                    "code": "TEXT_EXTRACTION_FAILED",
                    "message": "No text extracted from PDF",
                    "hint": "PDF might be scanned or image-based"
                }
            )

        # JD Part
        jobAgent = jdAgent.JobDescriptionAgent(llm_client=client)
        job_json = jobAgent.run(job_description)
        
        # Resume Part
        resume = resumeAgent.ResumeAgent(llm_client=client)
        return resume.run(text, job_json)
        
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "code": "RESUME_PROCESSING_ERROR",
                "message": "Failed to process resume",
                "details": str(e)
            }
        )