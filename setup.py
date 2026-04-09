import os
import django

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AutomatedAssessmentSystem.settings')
django.setup()

from django.core.management import call_command
from ARAS.models import User

def run_pipeline():
    print("🚀 Starting AFAS Hackathon Pipeline...")
    
    # 2. Make and Apply Migrations automatically
    print("📦 Building Database...")
    call_command('makemigrations', 'ARAS')
    call_command('migrate')
    
    # 3. Auto-Create Superadmin
    admin_email = "admin@afas.com"
    admin_password = "admin"
    
    if not User.objects.filter(email=admin_email).exists():
        print(f"🔑 Creating Superadmin: {admin_email}")
        User.objects.create_superuser(
            email=admin_email,
            password=admin_password,
            first_name="Super",
            last_name="Admin"
        )
        print("✅ Superadmin created successfully!")
    else:
        print("⚡ Superadmin already exists. Skipping.")
        
    print("\n🎉 Pipeline Complete! Run 'python manage.py runserver' to start.")

if __name__ == '__main__':
    run_pipeline()