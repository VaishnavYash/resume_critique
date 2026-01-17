
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
      return general_prompt(raw_text, schema, section_name, job_data, '''Rewrite the following EXPERIENCE bullets to be ATS-optimized''')
    
    case "projects":
      return general_prompt(raw_text, schema, section_name, job_data, '''Rewrite PROJECT descriptions bullets to align with the job description ''')

    case "skills":
      return skills_prompt(raw_text, job_data, schema)
    
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

def skills_prompt(resume_skills_text, job_description, schema):
    return f"""
You are cleaning and organizing SKILLS for an ATS-optimized resume.

SOURCE OF TRUTH:
- Resume skills text = the ONLY allowed skills
- Job description = relevance guidance ONLY

RESUME SKILLS (FACTS):
{resume_skills_text}

JOB DESCRIPTION (for relevance only):
{job_description}

TASK:
Return a cleaned, deduplicated, ATS-friendly list of skills using ONLY the skills explicitly present in the resume.

Return JSON in the following format:
{schema}

RULES (STRICT):
- DO NOT add skills from the job description
- DO NOT infer related technologies
- DO NOT expand acronyms unless explicitly written
- Normalize capitalization only (e.g., "rest api" → "REST API")
- Remove duplicates and irrelevant skills
- Preserve original meaning
- If no skills exist, return an empty array
- return atmost 10 skills in each category
- Ensure valid, parsable JSON
- Return ONLY valid JSON
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
  return f'''
  You are generating a NEW professional profile summary for a resume.

IMPORTANT:
- Do NOT rewrite or reference any existing summary.
- Generate the summary ONLY from experience, projects, and skills.

SOURCE OF TRUTH:
- Experience and project data = facts
- Skills list = allowed technologies
- Job description = role focus and keywords only

EXPERIENCE:
{experience_json}

PROJECTS:
{projects_json}

SKILLS:
{skills_list}

JOB DESCRIPTION:
{job_data}

TASK:
Generate a 2–3 line ATS-optimized professional summary.

RULES:
- Use only information present in the experience, projects, and skills
- Do NOT add new skills, tools, companies, or experience
- Align language with the job description
- Professional, concise, impact-focused tone
- No exaggeration or seniority inflation
- Do NOT mention years of experience unless explicitly stated
- Plain text only (no JSON, no bullets, no heading)
- Return raw JSON only.
- Do NOT include explanations, markdown, or code fences.
'''