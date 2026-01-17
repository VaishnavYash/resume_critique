from config import schema, prompts
from utils import pdf_text_organize as pdfOrganize, utils

class ResumeAgent:
    def __init__(self, llm_client):
        self.client = llm_client

    def normalize(self, text):
        return pdfOrganize.normalize_text(text)

    def split(self, text):
        return pdfOrganize.split_resume_sections(text)
    
    def structure_section(self, sections: dict[str, str], raw_text, passedSchema, section_name, jd):
        if not raw_text.strip():
            return {}

        prompt = prompts.organize_resume_content(raw_text, passedSchema, section_name, jd, sections["experience_raw"], sections["projects_raw"], sections["skills_raw"])
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Resume ATS Score Improving assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=schema.TEMPERATURES.get(section_name, 0.0),
            max_tokens=800
        )

        output = response.choices[0].message.content
        parsed = utils.safe_json_load(output)

        if parsed is not None:
            return parsed

        raise ValueError("LLM failed to return valid JSON")

    def run(self, resume_text, jd):
        normalized = self.normalize(resume_text)
        sections = self.split(normalized)
        
        # return {"sections": sections}
        
        # From JD
        personal = self.structure_section(sections,
            sections["personal_raw"], schema.PERSONAL_INFO_SCHEMA, "personal", jd
        )
        # print(f"Personal Section Structured : {personal}")
        
        # From JD
        summary = self.structure_section(sections, 
            sections["summary_raw"],schema.SUMMARY_SCHEMA, "summary", jd
        )
        
        # From Resume
        education = self.structure_section(sections,
            sections["education_raw"],schema.EDUCATION_SCHEMA, "education", jd
        )
        
        # From JD
        experience = self.structure_section(sections,
            sections["experience_raw"],schema.EXPERIENCE_SCHEMA, "experience", jd
        )
        
        # From JD
        projects = self.structure_section(sections,
            sections["projects_raw"], schema.PROJECTS_SCHEMA, "projects", jd
        )
        
        # From JD
        skills = self.structure_section(sections,
            sections["skills_raw"], schema.SKILLS_SCHEMA, "skills", jd
        )
        
        # From Resume
        achievement = self.structure_section(sections,
            sections["achievements_raw"], schema.ACHIEVEMENT_SCHEMA, "achievement", jd
        )

        return {
            "status": "success",
            "content": {
                "personal": personal.get("personal_info", []),
                "summary": summary.get("summary", []),
                "education": education.get("education", []),
                "experience": experience.get("experience", []),
                "projects": projects.get("projects", []),
                "skills": skills.get("skills", []),
                "achievement": achievement.get("achievement", []),
            }
        }