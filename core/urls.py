from django.urls import path
from . import views

urlpatterns = [
    # The homepage handles both GET (display) and POST (contact form submission)
    path('', views.home_view, name='home'), 
    # New endpoint for secure Gemini calls (ENSURE TRAILING SLASH)
    path('api/gemini-proxy/', views.gemini_proxy_view, name='gemini_proxy'),
]