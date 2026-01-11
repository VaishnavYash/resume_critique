SUMMARY_SCHEMA = """
{
  "summary": ""
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
      "description": [],
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

ACHIEVEMENT_SCHEMA = """
{
  "certificate": [],
  "general Points": ["",""]
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