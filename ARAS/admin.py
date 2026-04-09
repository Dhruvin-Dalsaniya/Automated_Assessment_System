# admin.py
from django.contrib import admin
from ARAS.models import QuestionSet, Question, JobRole, User

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
admin.site.register(User)