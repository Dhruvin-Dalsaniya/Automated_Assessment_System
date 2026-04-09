# admin.py
from django.contrib import admin
from django.utils.html import format_html
from ARAS.models import QuestionSet, Question, JobRole, User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 1. What shows up in the main list view
    list_display = ('email', 'first_name', 'last_name', 'job_role', 'status', 'colored_score_badge')
    list_filter = ('status', 'job_role')
    search_fields = ('email', 'first_name', 'last_name')
    
    # 2. Make the AI fields read-only so the admin can't fake the results
    readonly_fields = ('colored_score_badge', 'skills_gap_analysis', 'behavioral_summary')

    # 3. Organize the detail page into beautiful sections
    fieldsets = (
        ('Candidate Info', {
            'fields': ('email', 'first_name', 'last_name', 'uuid', 'password')
        }),
        ('Assessment Setup', {
            'fields': ('job_role', 'status', 'resume')
        }),
        ('🤖 AI Final Report Card', {
            'fields': ('colored_score_badge', 'behavioral_summary', 'skills_gap_analysis'),
            'classes': ('collapse',), # Makes it collapsible
        }),
    )

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

# # Register your User model too so you can manage candidates
# admin.site.register(User)