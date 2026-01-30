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

RESUME CONTENT:
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
      return general_prompt(raw_text, schema, section_name, job_data, '''Rewrite the following EXPERIENCE bullets to be ATS-optimized, Atmost 6 bullets per role. and each bullet must be atmost 25 words long''')
    
    case "projects":
      return general_prompt(raw_text, schema, section_name, job_data, '''Rewrite PROJECT descriptions bullets to align with the job description , Atmost 6 bullets per role. and each bullet must be atmost 25 words long''')

    case _:
          return f"""
      Derive ACHIEVEMENTS from the resume content.

      RESUME DATA:
      {raw_text}
      
      ATS KEYWORDS (HIGH PRIORITY):
      Required Skills:
      {job_data.get("required_skills", [])}

      Core Keywords:
      {job_data.get("core_keywords", [])}

      Preferred Skills (use only if implied):
      {job_data.get("preferred_skills", [])}
      
      Return JSON in the following format:
      {schema}

      RULES:
      - Atmost 5 achievement bullets
      - Each bullet must be atmost 25 words long
      - Use ONLY information present in the resume data
      - Achievements must be directly supported by resume content
      - Do NOT invent awards or metrics
      - Use concise bullet points
      - Return ONLY JSON
      - Return raw JSON only.
      - Do NOT include explanations, markdown, or code fences.
      """

def general_prompt(raw_text, schema, section_name, job_data, extra_prompt):
    # print(f'Job Data : {job_data}') 
    # print(f"\n required_skills: {job_data.get("required_skills", [])}")
    # print(f"\n preferred_skills: {job_data.get("preferred_skills", [])}")
    # print(f"\n core_keywords: {job_data.get("core_keywords", [])}\n")
    
    return f"""
You are rewriting a resume section for MAXIMUM ATS MATCH SCORE.
{extra_prompt}

SOURCE OF TRUTH:
- Resume data = factual constraints
- Job description = keyword source ONLY

SECTION: {section_name.upper()}

RESUME DATA (FACTS — do not contradict):
{raw_text}

ATS KEYWORDS (HIGH PRIORITY):
Required Skills:
{job_data.get("required_skills", [])}

Core Keywords:
{job_data.get("core_keywords", [])}

Preferred Skills (use only if implied):
{job_data.get("preferred_skills", [])}

PRIMARY OBJECTIVE:
Increase ATS keyword match score while preserving factual accuracy.

MANDATORY ATS RULES:
- Explicitly surface skills/tools that are CLEARLY IMPLIED by the resume text
- Prefer EXACT keyword phrases from the JD
- Repeat JD-critical keywords at least 2 times across bullets if supported
- Use canonical naming (e.g., "REST API" not "RESTful services")
- Avoid vague phrases (e.g., "worked on", "helped with")

YOU MUST:
- Rewrite every bullet (do NOT keep original wording)
- Use strong action verbs
- Make bullets results-oriented
- Embed JD keywords naturally but explicitly
- Merge weak bullets if needed
- Add up to 4 bullets ONLY if clearly implied

YOU MUST NOT:
- Invent tools, skills, companies, metrics, or timelines
- Add experience not supported by resume text
- Inflate seniority

FORMAT:
Return JSON ONLY in the following schema:
{schema}

STRICT OUTPUT RULES:
- Use ATS-friendly language
- Concise, scannable bullets
- Each bullet ≤ 25 words
- Valid JSON only
- No explanations, markdown, or comments
"""

def jd_extraction_prompt(job_description, schema):
    return f"""
You are extracting ATS-WEIGHTED KEYWORDS from a Job Description.

ATS ASSUMPTION:
- Required skills are hard filters
- Preferred skills are bonus points
- Core keywords affect relevance scoring
- ATS prefers EXACT lexical matches over paraphrases

JOB DESCRIPTION:
{job_description}

TASK:
Extract and classify keywords into ATS-weighted groups.

RETURN JSON ONLY in the following format:
{schema}

CLASSIFICATION RULES:
- REQUIRED SKILLS:
  - Must-have technical skills or tools
  - If missing, ATS score drops heavily
- PREFERRED SKILLS:
  - Nice-to-have tools or frameworks
  - Add bonus points if present
- CORE KEYWORDS:
  - Responsibilities, architectures, methodologies, concepts
  - Used for relevance scoring

STRICT RULES:
- Use EXACT wording from the JD
- Do NOT invent or infer skills
- Merge only truly identical terms
- Exclude soft skills
- Keep phrases 1–4 words max
- Valid JSON only
- No explanations, markdown, or comments
"""


def summary_prompt(experience_json, projects_json, skills_list, job_data):
  return f"""
You are generating an ATS-OPTIMIZED SUMMARY and SKILLS section.

THIS IS AN ATS-FIRST TASK, NOT A HUMAN-FIRST TASK.

SOURCE OF TRUTH:
- Experience & projects = factual constraints
- Resume skills list = allowed skill pool
- Job description = keyword priority ONLY

EXPERIENCE (FACTS):
{experience_json}

PROJECTS (FACTS):
{projects_json}

ALLOWED SKILLS (DO NOT ADD OUTSIDE THESE):
{skills_list}

JOB DESCRIPTION (KEYWORD PRIORITY):
{job_data}

TASKS:
1. Generate a 2–3 line summary optimized for ATS keyword density.
2. Reorganize skills to maximize ATS keyword matching.

ATS RULES (MANDATORY):
- Summary MUST include top JD keywords if supported by resume
- Skills MUST use exact JD terminology where possible
- Do NOT aggressively deduplicate JD keywords
- If a JD keyword exists in skills, ensure it appears verbatim
- Prefer repetition over elegance
- No seniority inflation
- No years unless explicitly stated

SKILLS RULES:
- Use clear ATS-standard categories (e.g., Programming Languages, Frameworks, Databases, Cloud & DevOps)
- Max 10 skills per category
- If category is empty, return empty array

OUTPUT FORMAT (STRICT):
Return valid JSON ONLY:
{schema.SUMMARY_SCHEMA}

FINAL RULES:
- Do NOT invent skills
- Do NOT infer from JD alone
- Ensure valid JSON
- Return raw JSON only
"""
