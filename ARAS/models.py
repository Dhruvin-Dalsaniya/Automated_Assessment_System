import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# --- 1. QUESTION SETS & QUESTIONS ---
class QuestionSet(models.Model):
    CATEGORY_CHOICES = (
        ('BEHAVIORAL', 'Behavioral'),
        ('APTITUDE', 'Aptitude'),
        ('TECHNICAL', 'Technical'),
        ('PEDAGOGY', 'Teaching/Pedagogy')
    )
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='BEHAVIORAL')

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class Question(models.Model):
    question_set = models.ForeignKey(QuestionSet, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    priority = models.IntegerField(default=1)

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return f"[Priority: {self.priority}] {self.text[:50]}"

# --- 2. JOB ROLE (DEFINED ONLY ONCE) ---
class JobRole(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    question_sets = models.ManyToManyField(QuestionSet, blank=True)

    def __str__(self):
        return self.title

# --- 3. CUSTOM USER MANAGER ---
class UserManager(BaseUserManager):
    def create_user(self, email, first_name="", last_name="", password=None):
        if not email:
            raise ValueError("Users must have an email")
        user = self.model(email=self.normalize_email(email), first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name="", last_name="", password=None):
        user = self.create_user(email, first_name, last_name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# --- 4. CUSTOM USER MODEL ---
class User(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = (
        ('AWAITING_UPLOAD', 'Awaiting Resume Upload'),
        ('IN_PROGRESS', 'Interview In Progress'),
        ('COMPLETED', 'Interview Completed')
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    # Django Admin Permissions
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # AFAS Fields
    job_role = models.ForeignKey(JobRole, on_delete=models.SET_NULL, null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AWAITING_UPLOAD')
    
    # Question Payloads
    hybrid_questions_payload = models.JSONField(null=True, blank=True)
    answers_payload = models.JSONField(null=True, blank=True)

    # --- MISSING AI FIELDS ADDED BACK HERE ---
    ai_overall_score = models.IntegerField(null=True, blank=True)
    skills_gap_analysis = models.TextField(null=True, blank=True)
    behavioral_summary = models.TextField(null=True, blank=True)
    # -----------------------------------------

    password = models.CharField(max_length=128, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()

    class Meta:
        indexes = [
            models.Index(fields=["email"], name="idx_users_email"),
            models.Index(fields=["uuid"], name="idx_users_uuid"),
        ]