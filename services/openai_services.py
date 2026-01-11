from openai import OpenAIError
from fastapi import HTTPException, status
from config import prompts, schema
from utils import utils

# Main function to get analysis of pdf
def getAPIResponse(file_content, job_role, company, client):
    try:
        file_content = file_content[:15000]  # SAFETY LIMIT

        prompt = prompts.build_resume_analysis_prompt(file_content, job_role, company)

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