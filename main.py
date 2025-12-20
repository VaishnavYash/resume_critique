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
    
# Main function to get API response
def getAPIResponse(file_content, job_role):
    try:
        
        return file_content
        # Create prompt for AI
        prompt = f"""Please analyze this resume and provide consructive feedback.
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience descriptions
        4. Specific improvements for {job_role if job_role else 'general job applications'}
        
        Resume Content: {file_content}
        
        Please Provide your analysis in a clear, structured format with specific recommendations."""
        
        client = OpenAI(api_key=openai_api_key)  # Initialize OpenAI client
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                # System message to set the context
                {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment."}, 
                
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
    job_role: str = Form("Software Engineer")
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

    return getAPIResponse(text, job_role)
