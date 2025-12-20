from pydantic import BaseModel

class ResumeRequest(BaseModel):
    resumeContent: str
    job_role: str