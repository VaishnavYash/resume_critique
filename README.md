AI Resume Critiquer
An AI-powered web application that analyzes resumes and provides constructive, role-specific feedback to help improve clarity, skills presentation, and overall impact.

Built using Streamlit, OpenAI, and Python.

🚀 Features
📄 Upload resumes in PDF or TXT format
🤖 AI-generated resume critique
🎯 Role-specific feedback based on the job you’re applying for
🧩 Structured analysis covering:
Content clarity & impact
Skills presentation
Experience descriptions
Actionable improvement suggestions
⚡ Simple, fast, and easy-to-use UI
🛠 Tech Stack
Python
Streamlit – Frontend UI
OpenAI API – AI-powered analysis
PyPDF2 – PDF text extraction
python-dotenv – Environment variable management
📂 Project Structure
├── app.py # Main Streamlit application ├── .env # Environment variables (not committed) ├── requirements.txt # Project dependencies ├── .gitignore └── README.md

🔐 Environment Setup
Create a .env file in the root directory and add your OpenAI API key: OPENAI_API_KEY=your_openai_api_key_here

⚠️ Important:
Add .env to .gitignore to avoid exposing your API key.


Command To Run the Code: d
# uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload