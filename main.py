import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, File, UploadFile, Form, HTTPException

from config import constants
from utils import text_extract_from_pdf as textFormat, utils
from services import openai_services as services

from core import new_resume_agent as resumeAgent, job_description_agent as jdAgent

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
    job_role: str = Form("Software Engineer"),
    company: str = Form("")
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

        return services.getAPIResponse(text, job_role, company, client)

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
    job_description: str = Form('''
            Tech Stack

Core: Node.js, React, TypeScript, AWS, MSSQL, Docker, CI/CD. Good to have .Net(C#) knowledge.

AI & Integration (Good to Have): Python, MCP, AWS Bedrock, LangGraph/Semantic Kernel, Vector Databases

Technical Skills

1-2 years of professional software development experience
Experience in Node.js, Python, React, JavaScript/TypeScript
 Good to have .Net (C#) knowledge.
Familiarity with REST APIs and API design
Understanding of relational databases (PostgreSQL , MSSQL or similar)
Experience with Git, Docker, and CI/CD pipelines
Familiarity with AWS or other cloud platforms
Understanding of authentication and authorization patterns
Problem-Solving & Learning

Open to learning new technologies and frameworks
Structured approach to solving technical problems
Comfortable with ambiguity and evolving requirements
Seeks feedback and iterates on solutions'''),
    # resume: UploadFile = File(...)
):
    try:
        # # file_bytes = await resume.read()

        # if not file_bytes:
        #     raise HTTPException(
        #         status_code=400,
        #         detail={
        #             "status": "error",
        #             "code": "EMPTY_FILE",
        #             "message": "Uploaded file is empty"
        #         }
        #     )

        # text =  textFormat.extract_text_from_pdf(file_bytes)

        # if not text.strip():
        #     raise HTTPException(
        #         status_code=422,
        #         detail={
        #             "status": "error",
        #             "code": "TEXT_EXTRACTION_FAILED",
        #             "message": "No text extracted from PDF",
        #             "hint": "PDF might be scanned or image-based"
        #         }
        #     )
            
    
        # JD Part
        # jobAgent = jdAgent.JobDescriptionAgent(llm_client=client)
        # job_json = jobAgent.run(job_description       )
        
        # Resume Part    
        resume = resumeAgent.ResumeAgent(llm_client=client)
        return resume.run(constants.tempNormalizedResume, constants.constJdOutput)

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