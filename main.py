from fastapi import Body, FastAPI, File, Form, UploadFile
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

from model.ResumeRequest import ResumeRequest

# Load environment variables from .env file
load_dotenv() 

# Initialize FastAPI app
app = FastAPI()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")  
        
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
You are an expert ATS resume reviewer and senior hiring manager.

Analyze the provided resume and return the response STRICTLY in valid JSON format.
Do NOT include markdown, explanations, or any text outside the JSON.
Do NOT wrap the JSON in code blocks.

Follow this exact JSON structure and key names:

{{
  "ats_score": number (0–100),
  "summary": string,
  "analysis": [
    {{
      "Content Clarity and Impact": {{
        "Strengths": [string, string],
        "Areas of Improvement": [string, string]
      }},
      "Skills Presentation": {{
        "Strengths": [string, string],
        "Areas of Improvement": [string, string]
      }},
      "Experience Descriptions": {{
        "Strengths": [string, string],
        "Areas of Improvement": [string, string]
      }},
      "Specific Improvements for {job_role} at {target_company}": {{
        "Technical Depth": [string, string],
        "Project Descriptions": [string, string],
        "Achievements": [string, string],
        "Certifications": [string, string]
      }},
      "Overall Recommendations": {{
        "Formatting": [string, string],
        "Tailoring": [string, string],
        "Proofreading": [string, string]
      }}
    }}
  ]
}}

Rules:
- All bullet points MUST be arrays of strings
- Tailor recommendations specifically for the target company’s hiring standards and expectations
- Keep points concise, actionable, and professional
- Do not hallucinate personal details
- Ensure valid, parsable JSON
- Return ONLY JSON, nothing else

Target Job Role:
{job_role}

Target Company:
{target_company}

Resume Content:
{resume_text}
""".strip()


# Main function to get API response
def getAPIResponse(file_content, job_role, company):
    try:
        # Create prompt for AI
        prompt = build_resume_analysis_prompt(file_content, job_role, company)
        
        client = OpenAI(api_key=openai_api_key)  # Initialize OpenAI client
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                # System message to set the context
                {"role": "system", "content": f"You are an expert resume reviewer with years of experience in HR and recruitment and is recruiting in the Company {company}."}, 
                
                # User message with the prompt
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,            
        )
        
        return response.choices[0].message.content  # Return the AI's response
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze_resume_pdf")
async def analyze_resume_pdf(
    resume: UploadFile = File(...),
    job_role: str = Form("Software Engineer"),
    company: str = Form("Software Engineer")
):
    file_bytes = await resume.read()
    print("PDF size (bytes):", len(file_bytes))

    text = extract_text_from_pdf(file_bytes)
    print("Extracted text length:", len(text))

    if not text.strip():
        return {
            "error": "No text extracted",
            "hint": "PDF might be scanned/image-based"
        }

    return getAPIResponse(text, job_role, company)
