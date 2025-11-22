from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages   # <-- IMPORTANT

from .forms import RegisterForm, StudentProfileForm, LoginForm
from .models import StudentProfile

import redis 


# --- HARD CODED REDIS CONFIG ---
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None  # set password here if you have one

# Create Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

from .llms import get_llm_result

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        profile_form = StudentProfileForm(request.POST)

        if form.is_valid() and profile_form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            messages.success(request, "Registration successful! Please login.")
            return redirect('login')

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = RegisterForm()
        profile_form = StudentProfileForm()

    return render(request, 'register.html', {
        'form': form,
        'profile_form': profile_form
    })

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)

                # LOGIN SUCCESS MESSAGE (optional)
                messages.success(request, f"Welcome back, {user.username}! 👋")

                return redirect('dashboard')
            else:
                # LOGIN ERROR MESSAGE
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
def dashboard_view(request):
    profile = StudentProfile.objects.get(user=request.user)
    if request.method == 'POST':
        sub = request.POST.get("subject")
        question = "question" , request.POST.get("question")
        learning_level = profile.learning_level
        full_name = profile.full_name
        grade = profile.grade
        medium = profile.medium
        payload = f"""
            Student Info:
            Full Name: {full_name}
            Grade: {grade}
            Medium: {medium}
            Learning Level: {learning_level}
            Subject: {sub}

            Question: {question}
        """
        import json
        res = get_llm_result(payload)
        answer = json.loads(res).get("html")
        redis_client.set("last_res" , answer)
        return render(request, 'dashboard.html', {'profile': profile , "answer":answer})

    return render(request, 'dashboard.html', {'profile': profile})


def logout_view(request):
    logout(request)

    # LOGOUT SUCCESS MESSAGE
    messages.info(request, "You have been logged out successfully.")

    return redirect("login")


# utils/pdf_generator.py
import pdfkit
import tempfile
from pathlib import Path

def html_to_pdf(html_content: str) -> Path:
    # Create a temporary file
    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_path = Path(tmp_pdf.name)
    pdfkit.from_string(html_content, str(pdf_path))
    return pdf_path


from django.http import FileResponse

def download_pdf(request):
    html_res = redis_client.get("last_res")
    pdf_path = html_to_pdf(html_res)
    print(html_res)
    return FileResponse(
        open(pdf_path, "rb"),
        as_attachment=True,
        filename="AI_Tutor_Answer.pdf",
        content_type="application/pdf",
    )


 