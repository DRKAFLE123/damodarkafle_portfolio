from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.mail import send_mail # Uncomment this for actual email functionality
from django.urls import reverse

def home_view(request):
    """
    Handles both displaying the portfolio page (GET) 
    and processing the contact form (POST).
    """
    if request.method == 'POST':
        # 1. Capture Form Data
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # NOTE ON EMAIL FUNCTIONALITY:
        # The logic here is simulated. For a real app, configure EMAIL_BACKEND in settings.py.
        
        print(f"--- New Message Received ---")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Message: {message[:50]}...")
        print("----------------------------")

        # After POST, redirect to the same page to prevent re-submission
        return HttpResponseRedirect(reverse('home') + '#contact')
    else:
        # Handle GET request (Render the homepage)
        return render(request, 'portfolio.html')