import os
import json
import requests
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt # <-- CRITICAL IMPORT
from django.urls import reverse
from django.contrib import messages
from .models import ContactMessage

# --- Gemini API Constants ---
# NOTE: GEMINI_API_KEY is loaded securely from your .env file
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_FALLBACK_API_KEY')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

def home_view(request):
    """
    Handles displaying the portfolio page (GET) and contact form submission (POST).
    """
    if request.method == 'POST':
        # Handles Contact Form Submission
        
        # 1. Capture Form Data
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_text = request.POST.get('message')
        
        # 2. Save to Database
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message_text
        )

        # 2b. Send notification email to site owner
        try:
            subject = f"New contact from {name or 'Website Visitor'}"
            body_lines = [
                f"Name: {name}",
                f"Email: {email}",
                "",
                "Message:",
                message_text or "(no message provided)",
            ]
            body = "\n".join(body_lines)

            send_mail(
                subject=subject,
                message=body,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                recipient_list=["damodarms0804@gmail.com"],
                fail_silently=False,
            )
        except Exception as e:
            # Log error but don't block the user flow
            print(f"Failed to send contact notification email: {e}")
        
        # 3. Add success message
        messages.success(request, "Thank you for your message, Damodar will be in touch soon!")

        # After POST, redirect to the same page to prevent re-submission
        return HttpResponseRedirect(reverse('home') + '#contact')
    else:
        # Handle GET request (Render the homepage)
        return render(request, 'portfolio.html')


@csrf_exempt # <-- THIS DECORATOR IS MANDATORY FOR THE PROXY VIEW
def gemini_proxy_view(request):
    """
    Proxies the Gemini API call securely from the server side.
    """
    if request.method == 'POST':
        try:
            # Check if the API key is set
            if not GEMINI_API_KEY or GEMINI_API_KEY == 'YOUR_FALLBACK_API_KEY':
                 return JsonResponse({'error': 'Gemini API Key is missing or invalid in .env file.'}, status=503)

            # Load JSON data from the request body
            data = json.loads(request.body)
            prompt = data.get('prompt')
            system_instruction = data.get('systemInstruction')

            if not prompt or not system_instruction:
                return HttpResponseBadRequest(json.dumps({'error': 'Missing prompt or system instruction'}), content_type='application/json')
            
            # 1. Construct the payload for Google's API
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "systemInstruction": {"parts": [{"text": system_instruction}]},
            }

            # 2. Make the secure API call using the server-side key
            headers = {
                'Content-Type': 'application/json'
            }
            
            # API key is appended to the URL securely
            api_response = requests.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", 
                headers=headers, 
                json=payload,
                timeout=15 
            )
            api_response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)

            # 3. Extract the generated text
            result = api_response.json()
            text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')

            if not text:
                return JsonResponse({'error': 'Gemini returned empty content.'}, status=500)

            # Return the result as JSON to the frontend
            return JsonResponse({'text': text})

        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({'error': 'Invalid JSON in request body'}), content_type='application/json')
        except requests.exceptions.RequestException as e:
            print(f"External API Request Failed: {e}")
            return JsonResponse({'error': f'External API request failed: {e}'}, status=500)
        except Exception as e:
            print(f"Unexpected Error in Proxy View: {e}")
            return JsonResponse({'error': f'An unexpected error occurred: {e}'}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)