SUMMARY_SCHEMA = """
{
  "summary": "",
  "skills": {
    "technical_skills": [],
    "tools_technologies": [],
    ...
  }
}
"""

EDUCATION_SCHEMA = """
{
  "education": [
    {
      "institution": "",
      "degree": "",
      "domain": "",
      "from": "",
      "to": "",
      "cgpa": ""
    }
  ]
}
"""

EXPERIENCE_SCHEMA = """
{
  "experience": [
    {
      "company": "",
      "role": "",
      "from": "",
      "to": "",
      "topic": "",
      "bullets": [],
      "location": ""
    }
  ]
}
"""

PROJECTS_SCHEMA = """
{
  "projects": [
    {
      "name": "",
      "description": [],
      "url": "",
      "tools": [],
      "location": "",
      "from": "",
      "to": ""
    }
  ]
}
"""

ACHIEVEMENT_SCHEMA = """
{
  "achievements": []
  }
"""

SECTION_KEYWORDS = {
    "summary": ["professional summary", "summary", "profile", "objective", "career objective", "professional profile"],
    "education": ["education", "academic", "qualifications", "educational background"],
    "experience": ["experience", "work experience", "employment", "professional experience"],
    "projects": ["projects", "personal projects", "project experience"],
    "skills": ["skills", "technical skills", "technologies", "tools", "programming languages"],
    "achievements": ["achievement", "achievements", "awards", "accomplishments", "certifications", "certificates", "honors", "recognitions", "notable", "distinctions"]
}

JD_SCHEMA = """
{
  "company": "",
  "role": string,
  "required_skills": [string],
  "preferred_skills": [string],
  "core_keywords": [string]
}
"""

TEMPERATURES = {
    "personal": 0.0,
    "education": 0.0,
    "skills": 0.0,
    "experience": 0.2,
    "projects": 0.2,
    "summary": 0.4,
    "achievement":0.0
}

PERSONAL_INFO_SCHEMA = """
{
  "personal_info": {
    "name": "",
    "email": "",
    "phone": "",
    "urls": [],
    "location": "",
    "designation": ""
  }
}
"""