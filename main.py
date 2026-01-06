import os
from openai import OpenAI, OpenAIError
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
import PyPDF2
import io


from model.ResumeRequest import ResumeRequest


# Load environment variables from .env file
# load_dotenv() 

# Initialize FastAPI app
app = FastAPI()

# Initialize OpenAI client
# openai_api_key = os.getenv("OPENAI_API_KEY")  # for system 

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

client = OpenAI(api_key=OPENAI_API_KEY)

        
# Function to extract text from PDF
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes), strict=False)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception:
        return ""


# Function to extract text from uploaded file (PDF or TXT)
def extract_text_from_file(uploaded_file):
    # If already text (local testing)
    if isinstance(uploaded_file, str):
        return uploaded_file

    file_bytes = uploaded_file.read()

    if uploaded_file.content_type == "application/pdf":
        return extract_text_from_pdf(file_bytes)

    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return ""
    
# Function to read local PDF file for testing
def read_local_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# Function to create prompt for AI
def build_resume_analysis_prompt(
    resume_text: str,
    job_role: str,
    target_company: str
) -> str:
    return f"""
You are an expert ATS resume reviewer and senior hiring manager in a company {target_company}.

Analyze the provided resume and return the response STRICTLY in valid JSON format.
Do NOT include markdown, explanations, or any text outside the JSON.
Do NOT wrap the JSON in code blocks.

Follow this exact JSON structure and key names:

{{
  "ats_score": number (0–100),
  "summary": string,
  "analysis": {{
    "Content Clarity and Impact": {{
      "Strengths": {{
        "data": List of String,
        "whyThisMatter": string
      }},
      "Areas of Improvement": {{
        "data": List of String,
        "whyThisMatter": string
      }}
    }},
    "Skills Presentation": {{
      "Strengths": {{
        "data": List of String,
        "whyThisMatter": string
      }},
      "Areas of Improvement": {{
        "data": List of String,
        "whyThisMatter": string
      }}
    }},
    "Experience Descriptions": {{
      "Strengths": {{
        "data": List of String,
        "whyThisMatter": string
      }},
      "Areas of Improvement": {{
        "data": List of String,
        "whyThisMatter": string
      }}
    }},
    "Specific Improvements for {job_role} at {target_company}": {{
      "Technical Depth": {{
        "data": List of String,
        "whyThisMatter": string
      }},
      "Project Descriptions": {{
        "data": List of String,
        "whyThisMatter": string
      }},
      "Achievements": {{
        "data": List of String,
        "whyThisMatter": string
      }},
      "Certifications": {{
        "data": List of String,
        "whyThisMatter": string
      }}
    }},
    "Overall Recommendations": {{
      "Formatting": {{
        "data": List of String,
        "whyThisMatter": string
      }},
      "Tailoring": {{
        "data": List of String,
        "whyThisMatter": string
      }},
      "Proofreading": {{
        "data": List of String,
        "whyThisMatter": string
      }}
    }}
  }}
}}

Rules:
- All bullet points MUST be arrays of strings
- Each "data" array MUST contain 2 to 4 concise bullet points
- Use professional, ATS-optimized language
- Tailor recommendations specifically for the target company’s hiring standards
- Do not hallucinate personal details
- Ensure valid, parsable JSON
- Return ONLY JSON
- Do NOT omit any section
- If information is missing, infer conservatively

Target Job Role:
{job_role}

Resume Content:
{resume_text}
""".strip()


MAX_CHARS = 15000  # ~8k tokens safety
# Main function to get API response
def getAPIResponse(file_content, job_role, company):
    try:
        file_content = file_content[:15000]  # SAFETY LIMIT

        prompt = build_resume_analysis_prompt(file_content, job_role, company)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are an expert resume reviewer for {company}."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200,
            timeout=40
        )

        return {
            "status": "success",
            "content": response.choices[0].message.content
        }

    except OpenAIError as e:
        raise HTTPException(
            status_code=502,
            detail={
                "status": "error",
                "code": "OPENAI_API_FAILURE",
                "message": "Failed to analyze resume",
                "details": str(e)
            }
        )

    # Unknown backend failure
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Something went wrong",
                "details": str(e)
            }
        )

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

        text = extract_text_from_pdf(file_bytes)

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

        return getAPIResponse(text, job_role, company)

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
        
        
# @app.get("/debug/network")
# def debug_network():
#     import requests
#     try:
#         r = requests.get("https://api.openai.com/v1/models", timeout=10)
#         return {
#             "reachable": True,
#             "status_code": r.status_code,
#             "headers": dict(r.headers)
#         }
#     except Exception as e:
#         return {
#             "reachable": False,
#             "error": str(e)
#         }
        
# @app.get("/debug/secret")
# def debug_secret():
#     key = os.getenv("OPENAI_API_KEY")
#     return {
#         "present": key is not None,
#         "length": len(key) if key else 0,
#         "starts_with_sk": key.startswith("sk-") if key else False,
#         "ends_with_newline": key.endswith("\n") if key else False
#     }


