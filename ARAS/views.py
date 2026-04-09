import fitz # PyMuPDF for reading PDFs
import random
from ARAS.models import *
# from .utils import gemini_api_call 

def process_resume_and_jumble_questions(session_id, uploaded_file):
    session = InterviewSession.objects.get(id=session_id)
    candidate = session.candidate
    job_role = candidate.job_role

    # 1. Save the file
    candidate.resume = uploaded_file
    candidate.save()

    # 2. Extract Text from PDF
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    resume_text = "".join([page.get_text() for page in pdf_document])

    # 3. Ask Gemini for Faculty-Specific Questions
    prompt = f"""
    You are an expert academic recruiter. Review the following resume for a {job_role.title} position.
    Generate 3 tough, highly specific interview questions based strictly on the candidate's stated experience, 
    research papers, or teaching history. Return ONLY a JSON list of strings.
    Resume Data: {resume_text}
    """
    
    # Call your LLM here (Simulated response below)
    # ai_questions_text = gemini_api_call(prompt)
    ai_questions_list = [
        {"text": "I see you published a paper on Machine Learning in 2024. How would you explain that to a freshman class?", "type": "ai"},
        {"text": "You mentored 5 post-grad students. How did you handle disputes regarding research authorship?", "type": "ai"}
    ]

    # 4. Fetch the Human (Static) Questions
    human_questions_list = job_role.static_questions 
    # Example: [{"text": "What is your core teaching philosophy?", "type": "human"}]

    # 5. Combine and Jumble (Shuffle)
    hybrid_assessment = ai_questions_list + human_questions_list
    random.shuffle(hybrid_assessment) # This mixes them up randomly!

    # 6. Save to session and update status
    session.hybrid_questions_payload = hybrid_assessment
    session.status = 'IN_PROGRESS'
    session.save()

    return hybrid_assessment