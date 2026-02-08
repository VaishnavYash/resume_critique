import os
# from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request


from config import constants
from utils import text_extract_from_pdf as textFormat, utils
from services import openai_services as services

from core import new_resume_agent as resumeAgent, job_description_agent as jdAgent


from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler, Limiter

# uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
def user_key(request):
    return request.headers.get("x-api-key") or get_remote_address(request)

limiter = Limiter(key_func=user_key)

# Load environment variables from .env file
# load_dotenv()

# Initialize FastAPI app
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

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
@limiter.limit("2/minute")
async def analyze_resume_pdf(
    request: Request, 
    resume: UploadFile = File(...),
    job_description: str = Form(constants.constJD)
):
    try:
        if resume.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "code": "EMPTY_FILE",
                    "message": "Only PDF files allowed"
                }
            )

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
@limiter.limit("2/minute")
async def get_pdf_content(
    request: Request,
    job_description: str = Form(constants.constJD),
    resume: UploadFile = File(...)
):
    try:
        if resume.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "code": "EMPTY_FILE",
                    "message": "Only PDF files allowed"
                }
            )
        
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