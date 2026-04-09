# admin.py
from django.contrib import admin
from django.utils.html import format_html
from ARAS.models import QuestionSet, Question, JobRole, User
from django.core.mail import send_mail 
from django.conf import settings 
import random 
import string
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 1. What shows up in the main list view
    list_display = ('email', 'first_name', 'last_name', 'job_role', 'status', 'colored_score_badge')
    list_filter = ('status', 'job_role')
    search_fields = ('email', 'first_name', 'last_name')
    
    # 2. Make the AI fields read-only so the admin can't fake the results
    readonly_fields = ('uuid','colored_score_badge', 'skills_gap_analysis', 'behavioral_summary')

    # 3. Organize the detail page into beautiful sections
    fieldsets = (
        ('Candidate Info', {
            'fields': ('email', 'first_name', 'last_name', 'uuid', 'password')
        }),
        ('Assessment Setup', {
            'fields': ('job_role', 'status', 'resume')
        }),
        ('AI Final Report Card', {
            'fields': ('colored_score_badge', 'behavioral_summary', 'skills_gap_analysis'),
            'classes': ('collapse',), # Makes it collapsible
        }),
    )
    def save_model(self, request, obj, form, change):
            is_new_candidate = obj.pk is None # Check if this is a brand new user
            
            # 1. Auto-generate a password if the admin left it blank
            if not obj.password:
                obj.password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                
            # 2. Save the user to the database
            super().save_model(request, obj, form, change)
            
            # 3. If new candidate and awaiting upload, send the email!
            if is_new_candidate and obj.status == 'AWAITING_UPLOAD':
                # Note: Change 5173 to whatever port your React app runs on
                react_frontend_url = f"http://localhost:5173/assessment/{obj.uuid}"
                role_title = obj.job_role.title if obj.job_role else "Faculty Position"
                
                subject = f"Invitation: AFAS AI Assessment for {role_title}"
                message = f"""Hello {obj.first_name},

    You have been invited to complete the AI-driven assessment for the {role_title} role.

    Your unique access link: {react_frontend_url}
    Your Login Password: {obj.password}

    Please log in and upload your resume to begin the evaluation.

    Best regards,
    The AFAS Recruitment Team"""

                try:
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [obj.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"⚠️ Email failed to send: {e}")
    # 4. The UI Hack: Injecting custom CSS/HTML into the Admin!
    def colored_score_badge(self, obj):
        if obj.ai_overall_score is None:
            return format_html('<span style="color: gray;">Pending</span>')
        
        # Color logic: Green for >80, Orange for 50-79, Red for <50
        if obj.ai_overall_score >= 80:
            color = "#28a745" # Green
        elif obj.ai_overall_score >= 50:
            color = "#ffc107" # Orange
        else:
            color = "#dc3545" # Red
            
        return format_html(
            f'<b style="color: white; background-color: {color}; padding: 4px 10px; border-radius: 12px; font-size: 14px;">'
            f'{obj.ai_overall_score}%'
            f'</b>'
        )
    colored_score_badge.short_description = 'AI Fit Score'
# @admin.register(Question)
# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ('text', 'question_set', 'priority')
#     list_filter = ('question_set',)

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3 # Shows 3 empty question rows by default for fast data entry

@admin.register(QuestionSet)
class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    inlines = [QuestionInline] # Puts questions directly inside the QuestionSet page!

@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ('title',)
    filter_horizontal = ('question_sets',) # Gives a beautiful dual-box UI to select sets

# Register your User model too so you can manage candidates
# admin.site.register(User)