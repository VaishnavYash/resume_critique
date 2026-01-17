import re
from config import schema

def normalize_text(text):
    text = text.replace("•", "-").replace("●", "-")
    text = text.replace("\r", "\n")
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r'\n{3,}', '\n\n', text)

    text = "\n".join(line.strip() for line in text.split("\n"))

    return text.strip()

def is_heading(line: str):
    original = line.strip()

    if not original:
        return None

    clean = original.lower()
    clean = re.sub(r':$', '', clean)  # remove trailing colon

    # Headings are usually short
    if len(clean) > 40:
        return None

    for section, keywords in schema.SECTION_KEYWORDS.items():
        for kw in keywords:
            # Case 1: Exact keyword match
            if clean == kw:
                return section

            # Case 2: Keyword followed by extra words (WORK EXPERIENCE)
            if clean.startswith(kw + " "):
                return section

            # Case 3: ALL CAPS short headings
            if original.isupper() and clean.replace(" ", "") == kw.replace(" ", ""):
                return section

    return None


def split_resume_sections(text: str):
    sections = {
        "personal_raw": "",
        "summary_raw": "",
        "education_raw": "",
        "experience_raw": "",
        "projects_raw": "",
        "skills_raw": "",
        "achievements_raw": ""
    }

    current_section = None
    
    is_heading_detected = False
    personal_section = ""

    for line in text.split("\n"):
        heading = is_heading(line)
        
        if(heading is not None):
            is_heading_detected = True 
            
        if(is_heading_detected == False):
            personal_section += line+ "\n"
                
        if heading:
            current_section = f"{heading}_raw"
            continue

        if current_section:
            sections[current_section] += line + "\n"

    sections["personal_raw"] = personal_section

    return {k: v.strip() for k, v in sections.items()}

