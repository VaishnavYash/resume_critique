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
      "bullets": []
    }
  ]
}
"""

PROJECTS_SCHEMA = """
{
  "projects": [
    {
      "name": "",
      "description": "",
      "tools": []
    }
  ]
}
"""

SKILLS_SCHEMA = """
{
  "skills": []
}
"""


SECTION_KEYWORDS = {
    "summary": ["professional summary", "summary", "profile", "objective"],
    "education": ["education", "academic"],
    "experience": ["experience", "work experience", "employment"],
    "projects": ["projects", "personal projects"],
    "skills": ["skills", "technical skills", "technologies"],
    "achievements": ["achievements", "awards", "accomplishments"]
}