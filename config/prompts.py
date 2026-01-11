
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
    "Specific Improvements for {job_role}": {{
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


def organize_resume_content(text, schema) :
    return f'''
    Below is the test which you need to infer:
    {text}
    
    produce me a json in the following format: 
    {schema}
    
    Rules:
    - Use professional, ATS-optimized language
    - If information is missing leave it as empty String
    - Do not hallucinate personal details
    - Ensure valid, parsable JSON
    - Return ONLY JSON
    '''