import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User
import anthropic
import json
from django.conf import settings
import json
import PyPDF2
import anthropic
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_context_decorator, method_decorator
from .models import User

# Disable CSRF for the hackathon so React can POST easily
@method_decorator(csrf_exempt, name='dispatch')
class UploadResumeView(View):
    def post(self, request, uuid):
        try:
            # 1. Get Candidate and Resume
            candidate = get_object_or_404(User, uuid=uuid)
            resume_file = request.FILES.get('resume')

            if not resume_file:
                return JsonResponse({"error": "No resume file provided"}, status=400)

            # 2. Save file and update status
            candidate.resume = resume_file
            candidate.status = 'IN_PROGRESS' # State change!
            candidate.save()

            # 3. Extract Text from PDF
            resume_text = ""
            try:
                pdf_reader = PyPDF2.PdfReader(resume_file)
                for page in pdf_reader.pages:
                    resume_text += page.extract_text() + "\n"
            except Exception as e:
                return JsonResponse({"error": f"Failed to read PDF: {str(e)}"}, status=400)

            # 4. Generate AI Round 3 Questions (Using Anthropic)
            job_title = candidate.job_role.title if candidate.job_role else "Faculty Member"
            
            # The Pre-defined AI Prompt
            prompt = f"""
            You are an expert academic interviewer hiring a {job_title}.
            Review the following candidate resume text.
            
            RESUME TEXT:
            {resume_text}
            
            Generate EXACTLY 2 highly specific, descriptive interview questions based ONLY on the experience, projects, or skills mentioned in this resume. 
            These questions should test their practical knowledge and teaching ability.
            
            Output ONLY a raw JSON array of objects. Do not include markdown formatting or backticks.
            Format exactly like this:
            [
              {{
                "id": 301,
                "question": "Your first custom question here?",
                "type": "text"
              }},
              {{
                "id": 302,
                "question": "Your second custom question here?",
                "type": "text"
              }}
            ]
            """

            # Call Claude 3 Haiku (Fast & Cheap)
            client = anthropic.Anthropic(api_key="sk-ant-your-key-here") # Hide in .env later!
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )

            # 5. Parse AI Response
            try:
                ai_questions = json.loads(message.content[0].text.strip())
            except Exception as e:
                print("JSON Parsing failed, falling back to default.", e)
                ai_questions = [
                    {"id": 301, "question": "Could you explain your most complex project to a beginner?", "type": "text"},
                    {"id": 302, "question": "Why are you interested in this specific role?", "type": "text"}
                ]

            # 6. Initialize the JSON Payload (We will fill Rounds 1 & 2 later)
            candidate.hybrid_questions_payload = {
                "round_1_mcq": [], # To be populated from database
                "round_2_descriptive": [], # To be populated from database
                "round_3_ai_dynamic": ai_questions
            }
            candidate.save()

            return JsonResponse({
                "message": "Resume uploaded successfully! AI has generated custom questions.",
                "status": candidate.status
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def generate_final_ai_report(candidate_name, job_role_title, answers_data):
    # Initialize Anthropic Client
    client = anthropic.Anthropic(api_key="sk-ant-your-key-here") # Hide this in .env later!
    
    # Format the answers
    dump_text = f"Candidate: {candidate_name}\nRole: {job_role_title}\n\nAnswers:\n"
    for item in answers_data:
        dump_text += f"Q: {item['question']}\nCandidate Answer: {item.get('answer', 'NO ANSWER PROVIDED')}\n\n"

    prompt = f"""
    You are an expert academic evaluator. Review the candidate's answers below.
    You MUST output ONLY a raw JSON object with no markdown formatting, no backticks, and no extra text.
    Format exactly like this:
    {{
        "ai_overall_score": 85,
        "skills_gap_analysis": "Short text about gaps.",
        "behavioral_summary": "Short text about behavior."
    }}
    
    Data to evaluate:
    {dump_text}
    """
    
    # Call Claude 3 Haiku (Fastest and cheapest for hackathons)
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.2, # Low temperature for strict JSON compliance
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Parse the response text safely
    try:
        response_text = message.content[0].text.strip()
        return json.loads(response_text)
    except Exception as e:
        print(f"Failed to parse Claude JSON: {e}")
        return {
            "ai_overall_score": 0,
            "skills_gap_analysis": "AI Parsing Error",
            "behavioral_summary": "AI Parsing Error"
        }

class FinalSubmitAssessmentView(APIView):
    def post(self, request, uuid_val):
        # 1. Identify Candidate
        user = get_object_or_404(User, uuid=uuid_val)
        
        # Expected frontend payload: 
        # {"answers": [{"question": "What is OOP?", "answer": "Object oriented..."}, ...]}
        submitted_answers = request.data.get('answers', [])
        
        if not submitted_answers:
            return Response({"error": "No answers submitted"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 2. Save the raw answers to the database just in case
        user.answers_payload = submitted_answers
        user.status = 'COMPLETED'
        
        # 3. Dump to LLM for Final Evaluation
        try:
            ai_report = generate_final_ai_report(
                candidate_name=f"{user.first_name} {user.last_name}",
                job_role_title=user.job_role.title if user.job_role else "Faculty",
                answers_data=submitted_answers
            )
            
            # 4. Save LLM results directly to the User model so Admin UI updates instantly
            user.ai_overall_score = ai_report.get('ai_overall_score')
            user.skills_gap_analysis = ai_report.get('skills_gap_analysis')
            user.behavioral_summary = ai_report.get('behavioral_summary')
            user.save()
            
            return Response({
                "message": "Assessment completed and AI evaluated successfully.",
                "report": ai_report
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Fallback save if LLM fails, so we don't lose the candidate's hard work
            user.save() 
            return Response({"error": f"LLM Evaluation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)