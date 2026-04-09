from django.urls import path
from . import views

urlpatterns = [
    # ---------------------------------------------------------
    # 1. AUTHENTICATION
    # Frontend hits this when the user clicks the email link.
    # Returns candidate details and whether they already uploaded a resume.
    # ---------------------------------------------------------
    path('api/auth/<uuid:uuid>/', views.VerifyCandidateView.as_view(), name='verify-candidate'),

    # ---------------------------------------------------------
    # 2. RESUME UPLOAD
    # Frontend sends the PDF here. Backend saves it and instantly 
    # sends it to Gemini to start generating Round 3 questions in the background.
    # ---------------------------------------------------------
    path('api/upload-resume/<uuid:uuid>/', views.UploadResumeView.as_view(), name='upload-resume'),

    # ---------------------------------------------------------
    # 3. FETCH ROUND QUESTIONS (Sequential)
    # Frontend requests: /api/questions/<uuid>/1/ (Gets 6 MCQs)
    # Frontend requests: /api/questions/<uuid>/2/ (Gets Descriptive)
    # Frontend requests: /api/questions/<uuid>/3/ (Gets AI Generated)
    # ---------------------------------------------------------
    # path('api/questions/<uuid:uuid>/<int:round_num>/', views.FetchRoundView.as_view(), name='fetch-round'),

    # ---------------------------------------------------------
    # 4. SUBMIT & EVALUATE
    # Frontend posts answers here after every round.
    # Backend marks correct/incorrect/skipped for Round 1.
    # On Round 3, it triggers the final Admin Report Card evaluation.
    # ---------------------------------------------------------
    # path('api/submit/<uuid:uuid>/<int:round_num>/', views.SubmitRoundView.as_view(), name='submit-round'),
]