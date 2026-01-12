from config import schema, prompts, constants
from utils import pdf_text_organize as pdfOrganize, utils

class JobDescriptionAgent:
    def __init__(self, llm_client):
        self.client = llm_client
    
    def normalize_skills(self, skills):
        return sorted({
            s.strip().upper()
            for s in skills
            if len(s.strip()) > 1
        })
        
    def remove_generic_keywords(self, keywords):
        GENERIC = {"communication", "teamwork", "collaboration"}

        filtered = []
        for k in keywords:
            if not any(g in k.lower() for g in GENERIC):
                filtered.append(k.strip())

        return filtered

            
    def call_open_ai_api(self, job_data):
        return constants.constJdOutput
        # if not job_data.strip():
        #     return {}
        # prompt = prompts.jd_extraction_prompt(job_data, schema.JD_SCHEMA)
        # response = self.client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=[
        #         {"role": "system", "content": "You are a Job Description parsing assistant."},
        #         {"role": "user", "content": prompt}
        #     ],
        #     temperature=0.0,
        #     max_tokens=800
        # )

        # output = response.choices[0].message.content
        # parsed = utils.safe_json_load(output)
        
        # if parsed is not None:
        #     return parsed

        # raise ValueError("LLM failed to return valid JSON")

    def run(self, job_data):
        api_response = self.call_open_ai_api(job_data)
        skills = self.normalize_skills(api_response.get("required_skills", []))
        keywords = self.remove_generic_keywords(api_response.get("keywords", []))

        
        return {
            "role": api_response.get("role", ""),
            "required_skills": skills,
            "keywords": keywords
        }

        