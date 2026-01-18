from config import schema

# Function to create prompt for AI
def build_resume_analysis_prompt(
    resume_text: str,
    job_json,
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
    "Specific Improvements for {job_json.get("role", [])}": {{
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
{job_json}

Resume Content:
{resume_text}
""".strip()


def organize_resume_content(raw_text, schema, section_name: str, job_data, experience_json, projects_json, skills_list):

  match section_name:
    case "personal":
      return f"""
        You are given RAW {section_name.upper()} TEXT from a resume.

        Text:
        {raw_text}

        Return JSON in the following format:
        {schema}

        Rules:
        - Use ONLY the given text
        - Capitalize proper nouns correctly
        - Do NOT add or infer information
        - If missing, use empty strings
        - Return ONLY valid JSON
        
        """
    
    case "summary":
      return summary_prompt(experience_json, projects_json, skills_list, job_data)
    
    case "education":
      return f"""
        You are given RAW {section_name.upper()} TEXT from a resume.

        Text:
        {raw_text}

        Return JSON in the following format:
        {schema}

        Rules:
        - Use ONLY the given text
        - Capitalize proper nouns correctly
        - Use consistent formatting for degrees and institutions
        - Do NOT add or infer information
        - If missing, use empty strings or empty arrays
        - Return ONLY valid JSON
        
        """
    
    case "experience":
      return general_prompt(raw_text, schema, section_name, job_data, '''Rewrite the following EXPERIENCE bullets to be ATS-optimized, Atmost 6 bullets per role. and each bullet must be atmost 20 words long''')
    
    case "projects":
      return general_prompt(raw_text, schema, section_name, job_data, '''Rewrite PROJECT descriptions bullets to align with the job description , Atmost 5 bullets per role. and each bullet must be atmost 20 words long''')

    case _:
          return f"""
      Derive ACHIEVEMENTS from the resume content.

      RESUME DATA:
      {raw_text}

      JOB DESCRIPTION CONTEXT:
      {job_data}
      
      Return JSON in the following format:
      {schema}

      RULES:
      - Atmost 4 achievement bullets
      - Each bullet must be atmost 20 words long
      - Use ONLY information present in the resume data
      - Achievements must be directly supported by resume content
      - Do NOT invent awards or metrics
      - Use concise bullet points
      - Return ONLY JSON
      - Return raw JSON only.
      - Do NOT include explanations, markdown, or code fences.
      """

def general_prompt(raw_text, schema, section_name, job_data, extra_prompt):
    return f"""
You are optimizing a resume for ATS screening. {extra_prompt}

SOURCE OF TRUTH (CRITICAL):
- Resume data = FACTS (must not change)
- Job description = KEYWORDS, LANGUAGE, EMPHASIS ONLY

SECTION TO OPTIMIZE: {section_name.upper()}

RESUME DATA (FACTS — do not invent beyond this):
{raw_text}

JOB DESCRIPTION (for keyword alignment only):
{job_data}

TASK (MANDATORY):
Rewrite and IMPROVE the resume content to better match the job description.

You MUST:
- Strengthen bullet points using action verbs
- Improve clarity and impact of each point
- Rephrase sentences to include relevant JD keywords
- Make responsibilities sound results-oriented
- Merge weak or redundant points if needed
- Add at most 4 bullets IF the resume text clearly implies them

You MUST NOT:
- Add new skills, tools, or technologies
- Add new companies, projects, roles, or experience
- Add years, metrics, or achievements not implied
- Change factual meaning

Return JSON in the following format:
{schema}

STRICT RULES:
- Use ONLY information present or clearly implied in resume data
- Rewording and restructuring is REQUIRED (do not return unchanged text)
- Use professional, ATS-friendly language
- Use power verbs (developed, implemented, optimized, delivered, etc.)
- Concise but impactful phrasing
- If information is missing, leave it empty
- Ensure valid, parsable JSON
- Return ONLY JSON
- Return raw JSON only.
- Do NOT include explanations, markdown, or code fences.
"""

def jd_extraction_prompt(job_description, schema):
    return f"""
You are extracting structured information from a Job Description.

JOB DESCRIPTION:
{job_description}

TASK:
Extract the following:
- Role / Job title
- Required technical skills
- Important ATS keywords (responsibilities, tools, concepts)

Return JSON in the following format:
{schema}

RULES:
- Do NOT invent skills not mentioned in the JD
- Merge similar skills (e.g., RESTful APIs → REST API)
- Exclude soft skills unless technical
- Keep skills concise (1–3 words)
- Keywords should be role-relevant phrases
- If something is missing, return empty values
- Return ONLY valid JSON
- Return raw JSON only.
- Do NOT include explanations, markdown, or code fences.
"""

def summary_prompt(experience_json, projects_json, skills_list, job_data):
  return f'''You are generating a NEW professional profile summary and cleaning SKILLS
for an ATS-optimized resume.

IMPORTANT:
- Do NOT rewrite or reference any existing summary.
- Generate a completely NEW summary.
- Skills must be selected ONLY from the resume skills text.
- This is a SYNTHESIS + ORGANIZATION task, NOT invention.

SOURCE OF TRUTH (STRICT):
- Experience and project data = FACTS (must not change)
- Resume skills text = ONLY allowed skills
- Job description = role focus and relevance guidance ONLY

EXPERIENCE (FACTS):
{experience_json}

PROJECTS (FACTS):
{projects_json}

RESUME SKILLS (ONLY THESE ARE ALLOWED):
{skills_list}

JOB DESCRIPTION (for relevance and wording only):
{job_data}

TASKS:
1. Generate a NEW 2–3 line ATS-optimized professional summary.
2. Clean, deduplicate, and organize the resume skills into ATS-friendly categories.

RULES (MANDATORY):
- Use ONLY information present in experience, projects, and resume skills
- Do NOT add new skills, tools, technologies, companies, roles, or experience
- Do NOT infer skills from the job description
- Do NOT expand acronyms unless explicitly written
- Normalize capitalization only (e.g., "rest api" → "REST API")
- Remove duplicates and clearly irrelevant skills
- Preserve original meaning of skills
- Return at most 10 skills per category
- Align summary language with the job description
- Professional, concise, impact-focused tone
- No exaggeration or seniority inflation
- Do NOT mention years of experience unless explicitly stated

OUTPUT FORMAT (STRICT):
Return valid JSON in the following format ONLY:
{schema.SUMMARY_SCHEMA}


OUTPUT RULES:
- Skills MUST come only from RESUME SKILLS text
- If a category has no skills, return an empty array
- Ensure valid, parsable JSON
- Return raw JSON only
- Do NOT include explanations, markdown, comments, or code fences
'''