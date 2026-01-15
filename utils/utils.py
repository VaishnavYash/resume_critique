import json
import re

def safe_json_load(text: str):
    if not text or not isinstance(text, str):
        return None

    # 1️⃣ Remove markdown fences
    cleaned = re.sub(r"```json|```", "", text).strip()

    # 2️⃣ Try direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 3️⃣ Extract first JSON object
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None

    return None
